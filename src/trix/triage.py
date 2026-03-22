"""
Triage Module

Risk-based prioritization and classification for incoming requests.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import numpy as np
import logging

logger = logging.getLogger(__name__)

DEFAULT_MINIMAL_RISK_THRESHOLD = 0.0
DEFAULT_LOW_RISK_THRESHOLD = 0.3
DEFAULT_MEDIUM_RISK_THRESHOLD = 0.5
DEFAULT_HIGH_RISK_THRESHOLD = 0.7
DEFAULT_CRITICAL_RISK_THRESHOLD = 0.9
DEFAULT_EMPTY_RISK_SCORE = 0.0


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
        enable_logging: bool = True,
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

        self.risk_thresholds = {
            RiskLevel.CRITICAL: DEFAULT_CRITICAL_RISK_THRESHOLD,
            RiskLevel.HIGH: DEFAULT_HIGH_RISK_THRESHOLD,
            RiskLevel.MEDIUM: DEFAULT_MEDIUM_RISK_THRESHOLD,
            RiskLevel.LOW: DEFAULT_LOW_RISK_THRESHOLD,
            RiskLevel.MINIMAL: DEFAULT_MINIMAL_RISK_THRESHOLD,
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

        timestamp = time.time()

        features = self._extract_features(input_data)
        risk_score = self._calculate_risk_score(features)

        risk_level = self._determine_risk_level(risk_score)

        if self.enable_logging:
            logger.info(f"Risk assessment: level={risk_level.name}, score={risk_score:.3f}")

        return TriageResult(
            risk_level=risk_level,
            risk_score=risk_score,
            features=features,
            metadata=input_data.get('metadata', {}),
            timestamp=timestamp,
        )

    def _extract_features(self, input_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract features from input data"""
        if "features" in input_data and isinstance(input_data["features"], dict):
            candidate_features = input_data["features"]
        else:
            candidate_features = input_data

        features: Dict[str, float] = {}

        for key, value in candidate_features.items():
            if isinstance(value, (int, float)):
                features[key] = float(value)

        return features

    def _calculate_risk_score(self, features: Dict[str, float]) -> float:
        """Calculate overall risk score from features"""
        if not features:
            return DEFAULT_EMPTY_RISK_SCORE

        if self.feature_weights:
            weighted_sum = sum(
                features.get(key, 0.0) * weight for key, weight in self.feature_weights.items()
            )
            total_weight = sum(self.feature_weights.values())
            return weighted_sum / total_weight if total_weight > 0 else DEFAULT_EMPTY_RISK_SCORE
        else:
            return float(np.mean(list(features.values())))

    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from score"""
        for level, threshold in sorted(
            self.risk_thresholds.items(), key=lambda x: x[1], reverse=True
        ):
            if risk_score >= threshold:
                return level
        return RiskLevel.MINIMAL

    def batch_assess(self, input_data_list: List[Dict[str, Any]]) -> List[TriageResult]:
        """Assess multiple inputs"""
        return [self.assess(data) for data in input_data_list]

    def update_thresholds(self, threshold_updates: Dict[RiskLevel, float]) -> None:
        """Update risk thresholds for the classifier."""
        self.risk_thresholds.update(threshold_updates)
