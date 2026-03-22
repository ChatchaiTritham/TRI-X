"""Integrated TRI-X pipeline."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .governance import GovernanceResult, SRGL
from .titrate import TemporalConstraint, TiTrATEEngine, TiTrATEResult
from .triage import RiskLevel, TriageModule, TriageResult
from .xai import Explanation, XAIInterface

logger = logging.getLogger(__name__)

PIPELINE_VERSION = "1.0"


@dataclass
class TRIXResult:
    """Complete TRI-X pipeline result."""

    triage: TriageResult
    titrate: Optional[TiTrATEResult]
    explanation: Explanation
    governance: GovernanceResult
    final_decision: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class TRIXPipeline:
    """Combine triage, governance, temporal execution, and explanation."""

    def __init__(
        self,
        triage_module: Optional[TriageModule] = None,
        titrate_engine: Optional[TiTrATEEngine] = None,
        xai_interface: Optional[XAIInterface] = None,
        governance: Optional[SRGL] = None,
        enable_logging: bool = True,
    ):
        self.triage = triage_module or TriageModule()
        self.titrate = titrate_engine or TiTrATEEngine()
        self.xai = xai_interface or XAIInterface()
        self.governance = governance or SRGL()
        self.enable_logging = enable_logging
        logger.info("TRIXPipeline initialized")

    def process(
        self,
        input_data: Dict[str, Any],
        action: Optional[Callable[..., Any]] = None,
        temporal_constraint: Optional[TemporalConstraint] = None,
    ) -> TRIXResult:
        """Process a single input through the full pipeline."""
        triage_result = self.triage.assess(input_data)
        governance_result = self.governance.screen(triage_result)

        titrate_result: Optional[TiTrATEResult] = None
        if action is not None and governance_result.approved:
            titrate_result = self.titrate.execute(action, temporal_constraint, input_data)

        explanation = self.xai.explain(input_data)
        final_decision = self._make_decision(triage_result, governance_result, titrate_result)

        pipeline_result = TRIXResult(
            triage=triage_result,
            titrate=titrate_result,
            explanation=explanation,
            governance=governance_result,
            final_decision=final_decision,
            metadata={
                "pipeline_version": PIPELINE_VERSION,
                "components": {
                    "triage": type(self.triage).__name__,
                    "titrate": type(self.titrate).__name__,
                    "xai": type(self.xai).__name__,
                    "governance": type(self.governance).__name__,
                },
            },
        )

        if self.enable_logging:
            logger.info(
                "TRI-X processing complete: decision=%s risk=%s approved=%s",
                final_decision,
                triage_result.risk_level.name,
                governance_result.approved,
            )

        return pipeline_result

    def _make_decision(
        self,
        triage_result: TriageResult,
        governance_result: GovernanceResult,
        titrate_result: Optional[TiTrATEResult],
    ) -> str:
        """Determine the final pipeline decision."""
        if not governance_result.approved:
            return "REJECTED"
        if triage_result.risk_level == RiskLevel.CRITICAL:
            return "ESCALATE_IMMEDIATE"
        if triage_result.risk_level == RiskLevel.HIGH:
            return "ESCALATE_URGENT"
        if triage_result.risk_level == RiskLevel.MEDIUM:
            return "REVIEW_REQUIRED"
        if titrate_result is not None and not titrate_result.constraint_met:
            return "TIMEOUT"
        return "APPROVED"

    def batch_process(self, input_batch: List[Dict[str, Any]]) -> List[TRIXResult]:
        """Process multiple inputs in batch."""
        return [self.process(input_data) for input_data in input_batch]

    def get_statistics(self) -> Dict[str, Any]:
        """Return pipeline component statistics."""
        return {
            "triage_thresholds": self.triage.risk_thresholds,
            "titrate": self.titrate.get_statistics(),
            "governance": {
                "policy": self.governance.screening_policy.value,
                "constraints": self.governance.constraints,
            },
        }
