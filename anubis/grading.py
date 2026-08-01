"""Privacy-preserving post-action grading for Anubis decisions."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from anubis.gate import GateValidationError


ASSESSMENTS = {"UPHELD", "OVERTURNED", "INCONCLUSIVE"}


def grade_result(
    result: dict[str, Any],
    *,
    assessment: str,
    assessor: str = "operator",
    note: str = "",
) -> dict[str, Any]:
    """Record an explicit post-action assessment without storing raw context.

    Grading is deliberately human/operator supplied. An outcome does not prove
    that a prior verdict was correct without an explicit assessment.
    """
    if result.get("verdict") not in {
        None,
        "SUPPORTED",
        "CONTRADICTED",
        "INSUFFICIENT_EVIDENCE",
        "UNAUTHORIZED",
        "NON_REPRODUCIBLE",
    }:
        raise GateValidationError("cannot grade unknown verdict")
    if assessment not in ASSESSMENTS:
        raise GateValidationError("invalid grade assessment")
    if not assessor or len(assessor) > 200:
        raise GateValidationError("assessor must be non-empty and at most 200 characters")
    note_hash = hashlib.sha256(note.encode()).hexdigest()[:16] if note else None
    return {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "packet_id": result.get("packet_id"),
        "packet_fingerprint": result.get("packet_fingerprint"),
        "verdict": result.get("verdict"),
        "assessment": assessment,
        "assessor": assessor,
        "note_code": note_hash,
    }


def append_grade(path: Path, grade: dict[str, Any]) -> None:
    """Append only the bounded grade record; never raw packet or outcome text."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(grade, sort_keys=True) + "\n")

