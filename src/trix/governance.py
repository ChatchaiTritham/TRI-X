"""Governance layer for TRI-X."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .triage import RiskLevel, TriageResult

logger = logging.getLogger(__name__)

DEFAULT_MAX_RISK_SCORE = 0.95
DEFAULT_MIN_CONFIDENCE = 0.6


class ScreeningPolicy(Enum):
    """Governance policy modes."""

    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    PERMISSIVE = "permissive"


@dataclass
class GovernanceResult:
    """Result of governance screening."""

    approved: bool
    risk_level: RiskLevel
    violations: List[str] = field(default_factory=list)
    constraints_met: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class SRGL:
    """Screening-first risk governance logic."""

    def __init__(
        self,
        screening_policy: ScreeningPolicy = ScreeningPolicy.CONSERVATIVE,
        enable_logging: bool = True,
    ):
        self.screening_policy = screening_policy
        self.enable_logging = enable_logging
        self.constraints = {
            "max_risk_score": DEFAULT_MAX_RISK_SCORE,
            "min_confidence": DEFAULT_MIN_CONFIDENCE,
            "require_explanation": True,
            "audit_critical": True,
        }
        logger.info("SRGL initialized with policy=%s", screening_policy.value)

    def screen(
        self,
        triage_result: TriageResult,
        additional_data: Optional[Dict[str, Any]] = None,
    ) -> GovernanceResult:
        """Screen a triage result through governance gates."""
        violation_messages: List[str] = []
        is_approved = True

        if triage_result.risk_score > self.constraints["max_risk_score"]:
            violation_messages.append(
                f"Risk score {triage_result.risk_score:.3f} exceeds maximum "
                f"{self.constraints['max_risk_score']:.3f}"
            )
            if self.screening_policy == ScreeningPolicy.CONSERVATIVE:
                is_approved = False

        if self.constraints["require_explanation"] and not triage_result.features:
            violation_messages.append("Missing explanation features")
            if self.screening_policy == ScreeningPolicy.CONSERVATIVE:
                is_approved = False

        if self.constraints["audit_critical"] and triage_result.risk_level == RiskLevel.CRITICAL:
            violation_messages.append("Critical risk requires audit trail")

        if self.screening_policy == ScreeningPolicy.CONSERVATIVE:
            if triage_result.risk_level in {RiskLevel.CRITICAL, RiskLevel.HIGH}:
                violation_messages.append(
                    f"Risk level {triage_result.risk_level.name} requires human review"
                )
                is_approved = False
        elif self.screening_policy == ScreeningPolicy.PERMISSIVE:
            is_approved = triage_result.risk_level != RiskLevel.CRITICAL

        constraints_met = len(violation_messages) == 0
        governance_result = GovernanceResult(
            approved=is_approved,
            risk_level=triage_result.risk_level,
            violations=violation_messages,
            constraints_met=constraints_met,
            metadata={
                "policy": self.screening_policy.value,
                "risk_score": triage_result.risk_score,
                "timestamp": triage_result.timestamp,
                "additional_data": additional_data or {},
            },
        )

        if self.enable_logging:
            logger.info(
                "SRGL screening: approved=%s violations=%s risk_level=%s",
                is_approved,
                len(violation_messages),
                triage_result.risk_level.name,
            )

        return governance_result

    def update_constraints(self, new_constraints: Dict[str, Any]) -> None:
        """Update governance constraints."""
        self.constraints.update(new_constraints)

    def set_policy(self, policy: ScreeningPolicy) -> None:
        """Change screening policy."""
        self.screening_policy = policy

    def audit_log(self, result: GovernanceResult) -> Dict[str, Any]:
        """Generate audit-log payload for a governance result."""
        return {
            "timestamp": result.metadata.get("timestamp"),
            "approved": result.approved,
            "risk_level": result.risk_level.name,
            "violations": result.violations,
            "policy": self.screening_policy.value,
            "constraints_met": result.constraints_met,
        }
