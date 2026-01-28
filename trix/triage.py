"""
Triage Module
=============

Risk-based prioritization and classification for incoming requests.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import numpy as np
import logging

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
 """Risk classification levels"""
 CRITICAL = 5
 HIGH = 4
 MEDIUM = 3
 LOW = 2
 MINIMAL = 1

@dataclass
class TriageResult:
 """Result of triage assessment"""
 risk_level: RiskLevel
 risk_score: float
 features: Dict[str, float]
 metadata: Dict[str, Any]
 timestamp: float

class TriageModule:
 """
 Risk-based triage module for classifying and prioritizing inputs.

 This module assesses incoming requests and assigns risk levels based on
 configurable thresholds and feature importance.
 """

 def __init__(
 self,
 threshold: float = 0.7,
 feature_weights: Optional[Dict[str, float]] = None,
 enable_logging: bool = True
 ):
 """
 Initialize triage module.

 Args:
 threshold: Base risk threshold (0-1)
 feature_weights: Custom weights for features
 enable_logging: Enable audit logging
 """
 self.threshold = threshold
 self.feature_weights = feature_weights or {}
 self.enable_logging = enable_logging

 # Default risk thresholds
 self.risk_thresholds = {
 RiskLevel.CRITICAL: 0.9,
 RiskLevel.HIGH: 0.7,
 RiskLevel.MEDIUM: 0.5,
 RiskLevel.LOW: 0.3,
 RiskLevel.MINIMAL: 0.0,
 }

 logger.info(f"TriageModule initialized with threshold={threshold}")

 def assess(self, input_data: Dict[str, Any]) -> TriageResult:
 """
 Assess risk level of input data.

 Args:
 input_data: Input features and metadata

 Returns:
 TriageResult with risk classification
 """
 import time

 # Extract features
 features = self._extract_features(input_data)

 # Calculate risk score
 risk_score = self._calculate_risk_score(features)

 # Classify risk level
 risk_level = self._classify_risk(risk_score)

 result = TriageResult(
 risk_level=risk_level,
 risk_score=risk_score,
 features=features,
 metadata=input_data.get("metadata", {}),
 timestamp=time.time()
 )

 if self.enable_logging:
 logger.info(
 f"Triage assessment: risk_level={risk_level.name}, "
 f"risk_score={risk_score:.3f}"
 )

 return result

 def _extract_features(self, input_data: Dict[str, Any]) -> Dict[str, float]:
 """Extract numerical features from input data"""
 features = {}

 if "features" in input_data:
 features = input_data["features"]
 else:
 # Extract from raw data
 for key, value in input_data.items():
 if isinstance(value, (int, float)):
 features[key] = float(value)
 elif isinstance(value, bool):
 features[key] = float(value)

 return features

 def _calculate_risk_score(self, features: Dict[str, float]) -> float:
 """Calculate weighted risk score"""
 if not features:
 return 0.0

 # Apply feature weights
 weighted_scores = []
 for feature_name, value in features.items():
 weight = self.feature_weights.get(feature_name, 1.0)
 weighted_scores.append(value * weight)

 # Normalize to [0, 1]
 risk_score = np.clip(np.mean(weighted_scores), 0.0, 1.0)
 return float(risk_score)

 def _classify_risk(self, risk_score: float) -> RiskLevel:
 """Classify risk level based on thresholds"""
 for level in [
 RiskLevel.CRITICAL,
 RiskLevel.HIGH,
 RiskLevel.MEDIUM,
 RiskLevel.LOW,
 RiskLevel.MINIMAL,
 ]:
 if risk_score >= self.risk_thresholds[level]:
 return level

 return RiskLevel.MINIMAL

 def batch_assess(self, inputs: List[Dict[str, Any]]) -> List[TriageResult]:
 """Assess multiple inputs in batch"""
 return [self.assess(input_data) for input_data in inputs]

 def update_thresholds(self, new_thresholds: Dict[RiskLevel, float]):
 """Update risk classification thresholds"""
 self.risk_thresholds.update(new_thresholds)
 logger.info(f"Risk thresholds updated: {new_thresholds}")
