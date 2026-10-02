"""Clinical TiTrATE phenotyping for TRI-X.

TiTrATE means Timing, Triggers, And Targeted Examination.  This module does
not use the term TiTrATE for execution timeouts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class DataQuality(Enum):
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    CONTRADICTORY = "contradictory"


@dataclass
class TiTrATEResult:
    """Structured clinical TiTrATE representation."""

    timing: Dict[str, Any]
    triggers: Dict[str, Any]
    targeted_examination: Dict[str, Any]
    syndrome: str
    missing_safety_fields: List[str] = field(default_factory=list)
    uncertainty_reasons: List[str] = field(default_factory=list)
    data_quality: DataQuality = DataQuality.INCOMPLETE
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def requires_uncertainty_escalation(self) -> bool:
        """Unknown safety-critical data must never support a downgrade."""
        return bool(self.missing_safety_fields or self.uncertainty_reasons)


class TiTrATEEngine:
    """Structure dizziness/vertigo history using clinical TiTrATE."""

    DEFAULT_SAFETY_FIELDS = (
        "new_focal_neurologic_deficit",
        "unable_to_walk_or_stand",
        "new_severe_headache_or_neck_pain",
        "syncope_or_loss_of_consciousness",
    )

    def __init__(self, safety_fields: List[str] | None = None):
        self.safety_fields = tuple(safety_fields or self.DEFAULT_SAFETY_FIELDS)

    def assess(self, input_data: Dict[str, Any]) -> TiTrATEResult:
        """Create a TiTrATE phenotype while preserving unknown values."""
        timing = dict(input_data.get("timing") or {})
        triggers = dict(input_data.get("triggers") or {})
        examination = dict(input_data.get("targeted_examination") or {})

        missing = [
            name for name in self.safety_fields
            if input_data.get(name) is None
        ]
        uncertainty = list(input_data.get("uncertainty_reasons") or [])

        syndrome = self._classify_syndrome(timing, triggers)
        quality = (
            DataQuality.COMPLETE
            if timing and "onset" in timing and not missing and not uncertainty
            else DataQuality.INCOMPLETE
        )

        return TiTrATEResult(
            timing=timing,
            triggers=triggers,
            targeted_examination=examination,
            syndrome=syndrome,
            missing_safety_fields=missing,
            uncertainty_reasons=uncertainty,
            data_quality=quality,
            metadata={
                "framework": "Timing-Triggers-And-Targeted Examination",
                "patient_reported_exam_restriction": (
                    "Targeted examination findings must identify their source; "
                    "clinician-only examinations must not be inferred from patient self-report."
                ),
            },
        )

    @staticmethod
    def _classify_syndrome(
        timing: Dict[str, Any], triggers: Dict[str, Any]
    ) -> str:
        """Conservative syndrome structuring; unknown remains unknown."""
        pattern = str(timing.get("pattern", "")).strip().lower()
        has_trigger = triggers.get("present")

        if pattern in {"continuous", "persistent", "acute_continuous"}:
            return "acute_continuous"
        if pattern in {"episodic", "recurrent"} and has_trigger is True:
            return "triggered_episodic"
        if pattern in {"episodic", "recurrent"} and has_trigger is False:
            return "spontaneous_episodic"
        return "undetermined"
