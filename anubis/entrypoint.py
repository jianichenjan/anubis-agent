#!/usr/bin/env python3
"""Single fail-closed entry point for Anubis review and enforcement."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from anubis.gate import (
    GateValidationError,
    _load_json,
    append_ledger,
    evaluate,
    should_summon,
    validate_packet,
)
from anubis.summon import ROOT, build_review_request


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--verdict", type=Path)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--contract", type=Path, default=ROOT / "ANUBIS.md")
    args = parser.parse_args()

    try:
        packet = _load_json(args.packet)
        validate_packet(packet)

        if not args.verdict:
            if not should_summon(packet):
                print(json.dumps({
                    "allowed": True,
                    "gate_mode": "advisory",
                    "packet_id": packet["packet_id"],
                    "summoned": False,
                }, sort_keys=True))
                return 0
            contract = args.contract.read_text(encoding="utf-8")
            print(build_review_request(packet, contract), end="")
            return 3

        verdict = _load_json(args.verdict)
        result = evaluate(packet, verdict)
        if args.ledger:
            append_ledger(args.ledger, result)
        print(json.dumps(result, sort_keys=True))
        return 0 if result["allowed"] else 2
    except (OSError, json.JSONDecodeError, GateValidationError) as exc:
        print(json.dumps({"allowed": False, "error": str(exc)}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
