#!/usr/bin/env python3
"""Deterministic enforcement gate for Anubis verdicts.

The gate validates a deliberately narrow subset of the JSON schemas without
third-party dependencies. It stores only fingerprints and verdict metadata in
its optional JSONL ledger; raw claims and evidence never enter the ledger.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERDICTS = {
    "SUPPORTED",
    "CONTRADICTED",
    "INSUFFICIENT_EVIDENCE",
    "UNAUTHORIZED",
    "NON_REPRODUCIBLE",
}

MANDATORY_ACTIONS = {
    "memory_write",
    "production_deploy",
    "database_migration",
    "authentication_change",
    "authorization_change",
    "rls_change",
    "tenant_boundary_change",
    "external_message",
    "public_claim",
    "credential_change",
    "permission_change",
    "integration_change",
    "destructive_action",
    "cross_vertical_decision",
}

MANDATORY_RISK_SIGNALS = {
    "evidence_contradiction",
    "authority_expansion",
    "sandbox_divergence",
    "tenant_leakage",
    "provenance_failure",
    "irreversible_consequence",
    "trajectory_escalation",
    "coercive_reframing",
}

SAFE_ACTIONS = {
    "read_only",
    "ordinary_explanation",
    "reversible_local_edit",
    "isolated_test",
}

PACKET_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{7,127}$")
EVIDENCE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


class GateValidationError(ValueError):
    """Raised when a packet or verdict violates the gate contract."""


def should_summon(packet: dict[str, Any]) -> bool:
    """Return whether the packet crosses an automatic Anubis trigger."""
    action = packet.get("proposed_action", {})
    kind = action.get("kind")
    risk_signals = set(packet.get("risk_signals", []))
    blast_radius = packet.get("blast_radius", {})
    reversal = packet.get("reversal", {})

    if kind in MANDATORY_ACTIONS:
        return True
    if risk_signals & MANDATORY_RISK_SIGNALS:
        return True
    if blast_radius.get("level") in {"cross_tenant", "production"}:
        return True
    if blast_radius.get("external") is True:
        return True
    if reversal.get("available") is False:
        return True
    return False


def validate_packet(packet: dict[str, Any]) -> None:
    _require_exact_keys(
        packet,
        required={
            "packet_id",
            "claim",
            "evidence",
            "proposed_action",
            "authority",
            "blast_radius",
            "reversal",
            "reproducibility",
            "persuasive_context_included",
        },
        optional={"risk_signals", "accepted_risks"},
        label="packet",
    )
    _require_pattern(packet["packet_id"], PACKET_ID_RE, "packet_id")
    _require_string(packet["claim"], "claim", 1, 4000)
    if packet["persuasive_context_included"] is not False:
        raise GateValidationError("packet is contaminated by persuasive context")

    evidence = packet["evidence"]
    if not isinstance(evidence, list) or len(evidence) > 100:
        raise GateValidationError("evidence must be an array of at most 100 items")
    evidence_ids: set[str] = set()
    for index, item in enumerate(evidence):
        _require_exact_keys(
            item,
            required={
                "evidence_id",
                "source",
                "locator",
                "observed_at",
                "relation",
                "sha256",
            },
            optional=set(),
            label=f"evidence[{index}]",
        )
        _require_pattern(item["evidence_id"], EVIDENCE_ID_RE, "evidence_id")
        if item["evidence_id"] in evidence_ids:
            raise GateValidationError("duplicate evidence_id")
        evidence_ids.add(item["evidence_id"])
        _require_string(item["source"], "source", 1, 500)
        _require_string(item["locator"], "locator", 1, 1000)
        _require_datetime(item["observed_at"], "observed_at")
        if item["relation"] not in {"supports", "contradicts", "context"}:
            raise GateValidationError("invalid evidence relation")
        _require_pattern(item["sha256"], SHA256_RE, "sha256")

    action = packet["proposed_action"]
    _require_exact_keys(
        action,
        required={"kind", "target", "summary"},
        optional=set(),
        label="proposed_action",
    )
    _require_string(action["kind"], "action kind", 1, 80)
    _require_string(action["target"], "action target", 1, 500)
    _require_string(action["summary"], "action summary", 1, 2000)

    authority = packet["authority"]
    _require_exact_keys(
        authority,
        required={"actor", "scope", "confirmed"},
        optional=set(),
        label="authority",
    )
    _require_string(authority["actor"], "authority actor", 1, 200)
    _require_string(authority["scope"], "authority scope", 1, 1000)
    _require_bool(authority["confirmed"], "authority confirmed")

    blast = packet["blast_radius"]
    _require_exact_keys(
        blast,
        required={"level", "tenant_ids", "external"},
        optional=set(),
        label="blast_radius",
    )
    if blast["level"] not in {"none", "local", "tenant", "cross_tenant", "production"}:
        raise GateValidationError("invalid blast-radius level")
    _require_unique_strings(blast["tenant_ids"], "tenant_ids", max_items=100)
    _require_bool(blast["external"], "blast-radius external")

    reversal = packet["reversal"]
    _require_exact_keys(
        reversal,
        required={"available", "procedure"},
        optional=set(),
        label="reversal",
    )
    _require_bool(reversal["available"], "reversal available")
    _require_string(reversal["procedure"], "reversal procedure", 0, 2000)
    if reversal["available"] and not reversal["procedure"].strip():
        raise GateValidationError("available reversal requires a procedure")

    reproducibility = packet["reproducibility"]
    _require_exact_keys(
        reproducibility,
        required={"required", "verified", "method"},
        optional=set(),
        label="reproducibility",
    )
    _require_bool(reproducibility["required"], "reproducibility required")
    _require_bool(reproducibility["verified"], "reproducibility verified")
    _require_string(reproducibility["method"], "reproducibility method", 0, 2000)
    if reproducibility["verified"] and not reproducibility["method"].strip():
        raise GateValidationError("verified reproducibility requires a method")

    risks = packet.get("risk_signals", [])
    _require_unique_strings(risks, "risk_signals", max_items=20)
    unknown_risks = set(risks) - MANDATORY_RISK_SIGNALS
    if unknown_risks:
        raise GateValidationError(f"unknown risk signal: {sorted(unknown_risks)[0]}")

    accepted_risks = packet.get("accepted_risks", [])
    if not isinstance(accepted_risks, list) or len(accepted_risks) > 100:
        raise GateValidationError("accepted_risks must be an array of at most 100 items")
    risk_ids: set[str] = set()
    for index, item in enumerate(accepted_risks):
        _require_exact_keys(
            item,
            required={"risk_id", "statement", "accepted_by", "scope", "accepted_at", "expires_at"},
            optional=set(),
            label=f"accepted_risks[{index}]",
        )
        _require_pattern(item["risk_id"], EVIDENCE_ID_RE, "risk_id")
        if item["risk_id"] in risk_ids:
            raise GateValidationError("duplicate risk_id")
        risk_ids.add(item["risk_id"])
        _require_string(item["statement"], "accepted-risk statement", 1, 1000)
        _require_string(item["accepted_by"], "accepted-risk authority", 1, 200)
        _require_string(item["scope"], "accepted-risk scope", 1, 1000)
        _require_datetime(item["accepted_at"], "accepted_at")
        if item["expires_at"] is not None:
            _require_datetime(item["expires_at"], "expires_at")


def validate_verdict(verdict: dict[str, Any], packet: dict[str, Any]) -> None:
    _require_exact_keys(
        verdict,
        required={
            "packet_id",
            "reviewer",
            "verdict",
            "evidence_ids",
            "findings",
            "missing_evidence",
            "reproducible",
            "conditions",
        },
        optional=set(),
        label="verdict",
    )
    if verdict["packet_id"] != packet["packet_id"]:
        raise GateValidationError("verdict packet_id does not match evidence packet")
    if verdict["reviewer"] != "anubis":
        raise GateValidationError("reviewer must be anubis")
    if verdict["verdict"] not in VERDICTS:
        raise GateValidationError("invalid verdict")

    _require_unique_strings(verdict["evidence_ids"], "evidence_ids", max_items=100)
    known_ids = {item["evidence_id"] for item in packet["evidence"]}
    unknown_ids = set(verdict["evidence_ids"]) - known_ids
    if unknown_ids:
        raise GateValidationError(f"verdict cites unknown evidence: {sorted(unknown_ids)[0]}")
    _require_string_list(verdict["findings"], "findings")
    _require_string_list(verdict["missing_evidence"], "missing_evidence")
    _require_bool(verdict["reproducible"], "verdict reproducible")
    _require_string_list(verdict["conditions"], "conditions")


def evaluate(packet: dict[str, Any], verdict: dict[str, Any]) -> dict[str, Any]:
    """Validate and return the enforced gate result."""
    validate_packet(packet)
    validate_verdict(verdict, packet)

    reasons: list[str] = []
    action_kind = packet["proposed_action"]["kind"]
    summoned = should_summon(packet)

    if verdict["verdict"] != "SUPPORTED":
        reasons.append(f"anubis verdict is {verdict['verdict']}")
    if not packet["authority"]["confirmed"]:
        reasons.append("authority is not confirmed")
    if not packet["evidence"]:
        reasons.append("no evidence supplied")
    if verdict["missing_evidence"]:
        reasons.append("verdict names missing evidence")
    if verdict["conditions"]:
        reasons.append("verdict has unresolved conditions")
    if packet["reproducibility"]["required"]:
        if not packet["reproducibility"]["verified"] or not verdict["reproducible"]:
            reasons.append("required reproducibility is not verified")
    if verdict["verdict"] == "SUPPORTED":
        cited = {
            item["evidence_id"]: item
            for item in packet["evidence"]
            if item["evidence_id"] in verdict["evidence_ids"]
        }
        if not any(item["relation"] == "supports" for item in cited.values()):
            reasons.append("supported verdict cites no supporting evidence")
        contradicting = [
            item["evidence_id"]
            for item in packet["evidence"]
            if item["relation"] == "contradicts"
        ]
        if contradicting:
            reasons.append("supported verdict leaves contradictory evidence unresolved")

    allowed = not reasons
    if action_kind in SAFE_ACTIONS and not summoned:
        gate_mode = "advisory"
    else:
        gate_mode = "mandatory"

    return {
        "packet_id": packet["packet_id"],
        "packet_fingerprint": packet_fingerprint(packet),
        "summoned": summoned,
        "gate_mode": gate_mode,
        "allowed": allowed,
        "verdict": verdict["verdict"],
        "reasons": reasons,
    }


def packet_fingerprint(packet: dict[str, Any]) -> str:
    canonical = json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical).hexdigest()


def append_ledger(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "packet_id": result["packet_id"],
        "packet_fingerprint": result["packet_fingerprint"],
        "summoned": result["summoned"],
        "gate_mode": result["gate_mode"],
        "allowed": result["allowed"],
        "verdict": result["verdict"],
        "reason_codes": [
            hashlib.sha256(reason.encode()).hexdigest()[:16]
            for reason in result["reasons"]
        ],
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise GateValidationError(f"{path}: top-level JSON must be an object")
    return value


def _require_exact_keys(
    value: Any,
    *,
    required: set[str],
    optional: set[str],
    label: str,
) -> None:
    if not isinstance(value, dict):
        raise GateValidationError(f"{label} must be an object")
    keys = set(value)
    missing = required - keys
    extra = keys - required - optional
    if missing:
        raise GateValidationError(f"{label} missing field: {sorted(missing)[0]}")
    if extra:
        raise GateValidationError(f"{label} has unknown field: {sorted(extra)[0]}")


def _require_string(value: Any, label: str, minimum: int, maximum: int) -> None:
    if not isinstance(value, str) or not minimum <= len(value) <= maximum:
        raise GateValidationError(f"{label} must be a string of length {minimum}..{maximum}")


def _require_pattern(value: Any, pattern: re.Pattern[str], label: str) -> None:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise GateValidationError(f"{label} has invalid format")


def _require_datetime(value: Any, label: str) -> None:
    if not isinstance(value, str):
        raise GateValidationError(f"{label} must be an ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise GateValidationError(f"{label} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise GateValidationError(f"{label} must include a timezone")


def _require_bool(value: Any, label: str) -> None:
    if not isinstance(value, bool):
        raise GateValidationError(f"{label} must be boolean")


def _require_unique_strings(value: Any, label: str, *, max_items: int) -> None:
    if (
        not isinstance(value, list)
        or len(value) > max_items
        or any(not isinstance(item, str) or not item for item in value)
        or len(value) != len(set(value))
    ):
        raise GateValidationError(f"{label} must contain unique non-empty strings")


def _require_string_list(value: Any, label: str) -> None:
    _require_unique_strings(value, label, max_items=100)
    if any(len(item) > 1000 for item in value):
        raise GateValidationError(f"{label} items must not exceed 1000 characters")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--verdict", type=Path, required=True)
    parser.add_argument("--ledger", type=Path)
    args = parser.parse_args()

    try:
        packet = _load_json(args.packet)
        verdict = _load_json(args.verdict)
        result = evaluate(packet, verdict)
        if args.ledger:
            append_ledger(args.ledger, result)
    except (OSError, json.JSONDecodeError, GateValidationError) as exc:
        print(json.dumps({"allowed": False, "error": str(exc)}, sort_keys=True))
        return 1

    print(json.dumps(result, sort_keys=True))
    return 0 if result["allowed"] else 2


if __name__ == "__main__":
    sys.exit(main())
