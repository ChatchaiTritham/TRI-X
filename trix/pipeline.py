"""
TRI-X Pipeline
==============

Integrated pipeline combining Triage, TiTrATE, XAI, and SRGL.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

from .triage import TriageModule, TriageResult, RiskLevel
from .titrate import TiTrATEEngine, TiTrATEResult, TemporalConstraint
from .xai import XAIInterface, Explanation, ExplanationMethod
from .governance import SRGL, GovernanceResult, ScreeningPolicy

logger = logging.getLogger(__name__)

@dataclass
class TRIXResult:
 """Complete TRI-X pipeline result"""
 triage: TriageResult
 titrate: Optional[TiTrATEResult]
 explanation: Explanation
 governance: GovernanceResult
 final_decision: str
 metadata: Dict[str, Any]

class TRIXPipeline:
 """
 TRI-X Integrated Pipeline.

 Combines Triage, TiTrATE, XAI, and SRGL governance into a
 comprehensive decision-making framework.
 """

 def __init__(
 self,
 triage_module: TriageModule,
 titrate_engine: TiTrATEEngine,
 xai_interface: XAIInterface,
 governance: SRGL,
 enable_logging: bool = True
 ):
 """
 Initialize TRI-X pipeline.

 Args:
 triage_module: Triage assessment module
 titrate_engine: TiTrATE execution engine
 xai_interface: XAI explanation interface
 governance: SRGL governance layer
 enable_logging: Enable pipeline logging
 """
 self.triage = triage_module
 self.titrate = titrate_engine
 self.xai = xai_interface
 self.governance = governance
 self.enable_logging = enable_logging

 logger.info("TRIXPipeline initialized")

 def process(
 self,
 input_data: Dict[str, Any],
 action: Optional[callable] = None,
 temporal_constraint: Optional[TemporalConstraint] = None
 ) -> TRIXResult:
 """
 Process input through complete TRI-X pipeline.

 Args:
 input_data: Input data to process
 action: Optional action to execute via TiTrATE
 temporal_constraint: Optional temporal constraint for action

 Returns:
 TRIXResult with complete pipeline output
 """
 # Step 1: Triage assessment
 logger.info("Step 1: Triage assessment")
 triage_result = self.triage.assess(input_data)

 # Step 2: SRGL screening
 logger.info("Step 2: SRGL governance screening")
 governance_result = self.governance.screen(triage_result)

 # Step 3: Execute action if approved and action provided
 titrate_result = None
 if action is not None:
 if governance_result.approved:
 logger.info("Step 3: TiTrATE action execution")
 titrate_result = self.titrate.execute(
 action,
 temporal_constraint,
 input_data
 )
 else:
 logger.warning("Action blocked by governance")

 # Step 4: Generate explanation
 logger.info("Step 4: XAI explanation generation")
 explanation = self.xai.explain(
 input_data,
 prediction=triage_result.risk_level.name,
 model=None
 )

 # Step 5: Make final decision
 final_decision = self._make_decision(
 triage_result,
 governance_result,
 titrate_result
 )

 result = TRIXResult(
 triage=triage_result,
 titrate=titrate_result,
 explanation=explanation,
 governance=governance_result,
 final_decision=final_decision,
 metadata={
 "pipeline_version": "1.0",
 "components": {
 "triage": type(self.triage).__name__,
 "titrate": type(self.titrate).__name__,
 "xai": type(self.xai).__name__,
 "governance": type(self.governance).__name__,
 }
 }
 )

 if self.enable_logging:
 logger.info(
 f"TRI-X processing complete: "
 f"decision={final_decision}, "
 f"risk={triage_result.risk_level.name}, "
 f"approved={governance_result.approved}"
 )

 return result

 def _make_decision(
 self,
 triage: TriageResult,
 governance: GovernanceResult,
 titrate: Optional[TiTrATEResult]
 ) -> str:
 """Make final decision based on all components"""
 if not governance.approved:
 return "REJECTED"

 if triage.risk_level == RiskLevel.CRITICAL:
 return "ESCALATE_IMMEDIATE"
 elif triage.risk_level == RiskLevel.HIGH:
 return "ESCALATE_URGENT"
 elif triage.risk_level == RiskLevel.MEDIUM:
 return "REVIEW_REQUIRED"
 elif titrate and not titrate.constraint_met:
 return "TIMEOUT"
 else:
 return "APPROVED"

 def batch_process(
 self,
 inputs: list[Dict[str, Any]]
 ) -> list[TRIXResult]:
 """Process multiple inputs in batch"""
 return [self.process(input_data) for input_data in inputs]

 def get_statistics(self) -> Dict[str, Any]:
 """Get pipeline statistics"""
 return {
 "triage": self.triage.__dict__,
 "titrate": self.titrate.get_statistics(),
 "governance": {
 "policy": self.governance.screening_policy.value,
 "constraints": self.governance.constraints,
 }
 }
