"""
SRGL - Screening-First Risk Governance Logic
=============================================

Governance layer ensuring safe and compliant decision-making.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

from .triage import RiskLevel, TriageResult

logger = logging.getLogger(__name__)

class ScreeningPolicy(Enum):
 """Screening policy modes"""
 CONSERVATIVE = "conservative" # Maximize safety
 BALANCED = "balanced" # Balance safety and efficiency
 PERMISSIVE = "permissive" # Maximize throughput

@dataclass
class GovernanceResult:
 """Result of governance screening"""
 approved: bool
 risk_level: RiskLevel
 violations: List[str]
 constraints_met: bool
 metadata: Dict[str, Any]

class SRGL:
 """
 Screening-First Risk Governance Logic.

 Implements pre-action screening to ensure all decisions meet
 safety, regulatory, and operational constraints before execution.
 """

 def __init__(
 self,
 screening_policy: ScreeningPolicy = ScreeningPolicy.CONSERVATIVE,
 enable_logging: bool = True
 ):
 """
 Initialize SRGL governance.

 Args:
 screening_policy: Policy for screening decisions
 enable_logging: Enable governance logging
 """
 self.screening_policy = screening_policy
 self.enable_logging = enable_logging

 # Define constraints
 self.constraints = {
 "max_risk_score": 0.95,
 "min_confidence": 0.6,
 "require_explanation": True,
 "audit_critical": True,
 }

 logger.info(
 f"SRGL initialized with policy={screening_policy.value}"
 )

 def screen(
 self,
 triage_result: TriageResult,
 additional_data: Optional[Dict[str, Any]] = None
 ) -> GovernanceResult:
 """
 Screen decision through governance gates.

 Args:
 triage_result: Triage assessment result
 additional_data: Additional context for screening

 Returns:
 GovernanceResult with approval status
 """
 violations = []
 approved = True

 # Gate 1: Risk score constraint
 if triage_result.risk_score > self.constraints["max_risk_score"]:
 violations.append(
 f"Risk score {triage_result.risk_score:.3f} exceeds "
 f"maximum {self.constraints['max_risk_score']}"
 )
 if self.screening_policy == ScreeningPolicy.CONSERVATIVE:
 approved = False

 # Gate 2: Critical risk escalation
 if triage_result.risk_level == RiskLevel.CRITICAL:
 if self.constraints["audit_critical"]:
 violations.append("Critical risk requires audit trail")
 # Don't block, but flag for review

 # Gate 3: Explanation requirement
 if self.constraints["require_explanation"]:
 if not triage_result.features:
 violations.append("Missing explanation features")
 if self.screening_policy == ScreeningPolicy.CONSERVATIVE:
 approved = False

 # Gate 4: Policy-specific constraints
 if self.screening_policy == ScreeningPolicy.CONSERVATIVE:
 # Conservative: Block high and critical risks without review
 if triage_result.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
 violations.append(
 f"Risk level {triage_result.risk_level.name} "
 f"requires human review in conservative mode"
 )

 elif self.screening_policy == ScreeningPolicy.PERMISSIVE:
 # Permissive: Only block critical violations
 approved = True # Override earlier blocks unless critical

 constraints_met = len(violations) == 0

 result = GovernanceResult(
 approved=approved,
 risk_level=triage_result.risk_level,
 violations=violations,
 constraints_met=constraints_met,
 metadata={
 "policy": self.screening_policy.value,
 "risk_score": triage_result.risk_score,
 "timestamp": triage_result.timestamp,
 }
 )

 if self.enable_logging:
 logger.info(
 f"SRGL screening: approved={approved}, "
 f"violations={len(violations)}, "
 f"risk_level={triage_result.risk_level.name}"
 )

 return result

 def update_constraints(self, new_constraints: Dict[str, Any]):
 """Update governance constraints"""
 self.constraints.update(new_constraints)
 logger.info(f"SRGL constraints updated: {new_constraints}")

 def set_policy(self, policy: ScreeningPolicy):
 """Change screening policy"""
 self.screening_policy = policy
 logger.info(f"SRGL policy changed to: {policy.value}")

 def audit_log(self, result: GovernanceResult) -> Dict[str, Any]:
 """Generate audit log entry"""
 return {
 "timestamp": result.metadata.get("timestamp"),
 "approved": result.approved,
 "risk_level": result.risk_level.name,
 "violations": result.violations,
 "policy": self.screening_policy.value,
 "constraints_met": result.constraints_met,
 }
