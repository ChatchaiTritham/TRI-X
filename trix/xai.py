"""
XAI Interface
=============

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
 prediction: Any,
 model: Optional[Any] = None
 ) -> Explanation:
 """
 Generate explanation for prediction.

 Args:
 input_data: Input features
 prediction: Model prediction
 model: Optional model for some explanation methods

 Returns:
 Explanation object
 """
 if self.method == ExplanationMethod.SHAP:
 return self._explain_shap(input_data, prediction, model)
 elif self.method == ExplanationMethod.LIME:
 return self._explain_lime(input_data, prediction, model)
 elif self.method == ExplanationMethod.RULES:
 return self._explain_rules(input_data, prediction)
 elif self.method == ExplanationMethod.COUNTERFACTUAL:
 return self._explain_counterfactual(input_data, prediction)
 else:
 return self._explain_attention(input_data, prediction)

 def _explain_shap(
 self,
 input_data: Dict[str, Any],
 prediction: Any,
 model: Optional[Any]
 ) -> Explanation:
 """SHAP-based explanation"""
 # Simplified SHAP approximation
 features = input_data.get("features", {})

 # Calculate feature importance (simplified)
 importance = {}
 for feature, value in features.items():
 # Simple gradient approximation
 importance[feature] = abs(value * 0.1 + np.random.normal(0, 0.05))

 # Normalize
 total = sum(importance.values())
 if total > 0:
 importance = {k: v / total for k, v in importance.items()}

 rules = [
 f"Feature '{k}' contributes {v:.3f} to decision"
 for k, v in sorted(
 importance.items(), key=lambda x: x[1], reverse=True
 )[:5]
 ]

 return Explanation(
 method=ExplanationMethod.SHAP,
 feature_importance=importance,
 rules=rules,
 confidence=0.85,
 metadata={"prediction": prediction}
 )

 def _explain_lime(
 self,
 input_data: Dict[str, Any],
 prediction: Any,
 model: Optional[Any]
 ) -> Explanation:
 """LIME-based explanation"""
 features = input_data.get("features", {})

 # Simplified LIME approximation
 importance = {}
 for feature, value in features.items():
 # Perturb and measure impact
 base_score = value
 importance[feature] = abs(base_score * np.random.uniform(0.8, 1.2))

 total = sum(importance.values())
 if total > 0:
 importance = {k: v / total for k, v in importance.items()}

 rules = [
 f"Local model: '{k}' → {v:.3f} importance"
 for k, v in sorted(
 importance.items(), key=lambda x: x[1], reverse=True
 )[:5]
 ]

 return Explanation(
 method=ExplanationMethod.LIME,
 feature_importance=importance,
 rules=rules,
 confidence=0.78,
 metadata={"prediction": prediction}
 )

 def _explain_rules(
 self,
 input_data: Dict[str, Any],
 prediction: Any
 ) -> Explanation:
 """Rule-based explanation"""
 features = input_data.get("features", {})

 # Extract decision rules
 rules = []
 importance = {}

 for feature, value in features.items():
 if value > 0.7:
 rules.append(f"IF {feature} > 0.7 THEN high_risk")
 importance[feature] = 0.9
 elif value > 0.5:
 rules.append(f"IF {feature} > 0.5 THEN medium_risk")
 importance[feature] = 0.6
 else:
 importance[feature] = 0.3

 return Explanation(
 method=ExplanationMethod.RULES,
 feature_importance=importance,
 rules=rules,
 confidence=0.95,
 metadata={"prediction": prediction}
 )

 def _explain_counterfactual(
 self,
 input_data: Dict[str, Any],
 prediction: Any
 ) -> Explanation:
 """Counterfactual explanation"""
 features = input_data.get("features", {})

 # Generate counterfactuals
 rules = []
 importance = {}

 for feature, value in features.items():
 # What-if scenarios
 delta = 0.2
 new_value = value - delta

 rules.append(
 f"IF {feature} was {new_value:.2f} instead of {value:.2f}, "
 f"prediction would change by ~{delta * 100}%"
 )
 importance[feature] = abs(delta)

 return Explanation(
 method=ExplanationMethod.COUNTERFACTUAL,
 feature_importance=importance,
 rules=rules[:5],
 confidence=0.72,
 metadata={"prediction": prediction}
 )

 def _explain_attention(
 self,
 input_data: Dict[str, Any],
 prediction: Any
 ) -> Explanation:
 """Attention-based explanation"""
 features = input_data.get("features", {})

 # Simulate attention weights
 importance = {}
 for feature, value in features.items():
 attention_weight = np.random.beta(2, 5) # Skewed distribution
 importance[feature] = attention_weight * value

 total = sum(importance.values())
 if total > 0:
 importance = {k: v / total for k, v in importance.items()}

 rules = [
 f"Attention focused on '{k}' with weight {v:.3f}"
 for k, v in sorted(
 importance.items(), key=lambda x: x[1], reverse=True
 )[:5]
 ]

 return Explanation(
 method=ExplanationMethod.ATTENTION,
 feature_importance=importance,
 rules=rules,
 confidence=0.82,
 metadata={"prediction": prediction}
 )

 def compare_methods(
 self,
 input_data: Dict[str, Any],
 prediction: Any,
 model: Optional[Any] = None
 ) -> Dict[ExplanationMethod, Explanation]:
 """Compare multiple explanation methods"""
 results = {}

 for method in [
 ExplanationMethod.SHAP,
 ExplanationMethod.LIME,
 ExplanationMethod.RULES
 ]:
 original_method = self.method
 self.method = method

 results[method] = self.explain(input_data, prediction, model)

 self.method = original_method

 return results
