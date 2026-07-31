"""Small provider-neutral integration helpers for Anubis."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from anubis.gate import (
    GateValidationError,
    append_ledger,
    evaluate,
    packet_fingerprint,
    should_summon,
    validate_packet,
)
from anubis.summon import build_review_request


class AnubisBlocked(RuntimeError):
    """Raised only when a caller explicitly asks to enforce a blocked result."""

    def __init__(self, result: dict[str, Any]) -> None:
        self.result = result
        super().__init__(
            f"Anubis blocked packet {result.get('packet_id')}: "
            + ", ".join(result.get("reasons", []))
        )


Reviewer = Callable[[str], dict[str, Any]]


def review_action(
    packet: dict[str, Any],
    reviewer: Reviewer,
    *,
    contract: str = "Review the proposed action independently.",
    ledger: Path | None = None,
) -> dict[str, Any]:
    """Review a packet and return a deterministic result.

    ``reviewer`` is the caller's model/provider adapter. This helper never
    executes the proposed action and never treats a review request as approval.
    """
    validate_packet(packet)
    if not should_summon(packet):
        result = {
            "packet_id": packet["packet_id"],
            "packet_fingerprint": packet_fingerprint(packet),
            "summoned": False,
            "gate_mode": "advisory",
            "allowed": True,
            "verdict": None,
            "reasons": [],
        }
        if ledger:
            append_ledger(ledger, result)
        return result

    verdict = reviewer(build_review_request(packet, contract))
    result = evaluate(packet, verdict)
    if ledger:
        append_ledger(ledger, result)
    return result


def enforce(result: dict[str, Any]) -> None:
    """Fail closed for callers that are ready to make the real change."""
    if not result.get("allowed"):
        raise AnubisBlocked(result)

