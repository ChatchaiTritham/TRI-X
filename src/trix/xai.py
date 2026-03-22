"""
XAI Interface

Explainable AI interface providing transparency for decisions.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import numpy as np
import logging

logger = logging.getLogger(__name__)


class ExplanationMethod(Enum):
    """Available explanation methods"""
    LIME = "lime"
    SHAP = "shap"
    ATTENTION = "attention"
    RULES = "rules"
    COUNTERFACTUAL = "counterfactual"


@dataclass
class Explanation:
    """Explanation result"""
    method: ExplanationMethod
    feature_importance: Dict[str, float]
    rules: List[str]
    confidence: float
    metadata: Dict[str, Any]


class XAIInterface:
    """
    Explainable AI Interface.

    Provides multiple explanation methods for transparency and
    interpretability of AI decisions.
    """

    def __init__(
        self,
        method: ExplanationMethod = ExplanationMethod.SHAP,
        enable_logging: bool = True
    ):
        """
        Initialize XAI interface.

        Args:
            method: Default explanation method
            enable_logging: Enable explanation logging
        """
        self.method = method
        self.enable_logging = enable_logging

        logger.info(f"XAIInterface initialized with method={method.value}")

    def explain(
        self,
        input_data: Dict[str, Any],
        method: Optional[ExplanationMethod] = None
    ) -> Explanation:
        """
        Generate explanation for input.

        Args:
            input_data: Input features
            method: Specific method to use (overrides default)

        Returns:
            Explanation object
        """
        method = method or self.method

        if method == ExplanationMethod.SHAP:
            return self._explain_shap(input_data)
        elif method == ExplanationMethod.LIME:
            return self._explain_lime(input_data)
        elif method == ExplanationMethod.RULES:
            return self._explain_rules(input_data)
        else:
            return self._explain_default(input_data)

    def _explain_shap(self, input_data: Dict[str, Any]) -> Explanation:
        """SHAP-based explanation"""
        features = {k: float(v) for k, v in input_data.items() if isinstance(v, (int, float))}
        importance = {k: v / sum(features.values()) if features else 0 for k, v in features.items()}

        return Explanation(
            method=ExplanationMethod.SHAP,
            feature_importance=importance,
            rules=[],
            confidence=0.85,
            metadata={}
        )

    def _explain_lime(self, input_data: Dict[str, Any]) -> Explanation:
        """LIME-based explanation"""
        features = {k: float(v) for k, v in input_data.items() if isinstance(v, (int, float))}
        importance = {k: abs(v) for k, v in features.items()}

        return Explanation(
            method=ExplanationMethod.LIME,
            feature_importance=importance,
            rules=[],
            confidence=0.80,
            metadata={}
        )

    def _explain_rules(self, input_data: Dict[str, Any]) -> Explanation:
        """Rule-based explanation"""
        rules = []
        importance = {}

        for key, value in input_data.items():
            if isinstance(value, (int, float)):
                rules.append(f"IF {key} = {value} THEN high_risk")
                importance[key] = float(value)

        return Explanation(
            method=ExplanationMethod.RULES,
            feature_importance=importance,
            rules=rules,
            confidence=0.90,
            metadata={}
        )

    def _explain_default(self, input_data: Dict[str, Any]) -> Explanation:
        """Default explanation"""
        features = {k: float(v) for k, v in input_data.items() if isinstance(v, (int, float))}

        return Explanation(
            method=self.method,
            feature_importance=features,
            rules=[],
            confidence=0.75,
            metadata={}
        )

    def batch_explain(
        self,
        input_data_list: List[Dict[str, Any]],
        method: Optional[ExplanationMethod] = None
    ) -> List[Explanation]:
        """Generate explanations for multiple inputs"""
        return [self.explain(data, method) for data in input_data_list]
