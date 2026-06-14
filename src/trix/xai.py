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
        enable_logging: bool = True,
        model: Optional[Any] = None,
        feature_names: Optional[List[str]] = None,
        background: Optional[Any] = None,
    ):
        """
        Initialize XAI interface.

        Args:
            method: Default explanation method
            enable_logging: Enable explanation logging
            model: Optional fitted tree model (e.g. a RandomForest) enabling genuine
                SHAP attributions via ``shap.TreeExplainer``.
            feature_names: Ordered feature names matching the model's input columns.
            background: Optional background sample (array-like) for the explainer.

        Notes:
            When ``model`` is supplied, :meth:`explain` computes real SHAP values from
            the fitted model. The full, model-backed SHAP/LIME/DiCE implementations
            used by the empirical pipeline live in ``trix.empirical.explain``.
        """
        self.method = method
        self.enable_logging = enable_logging
        self.model = model
        self.feature_names = feature_names
        self.background = background

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
        """SHAP-based explanation.

        When a fitted tree model was supplied at construction time, this computes
        genuine SHAP attributions for the instance via ``shap.TreeExplainer``.
        Without a model, it raises -- there is no honest SHAP value to return, so the
        caller should attach a model or use the ``empirical`` pipeline directly.
        """
        if self.model is None:
            raise ValueError(
                "Genuine SHAP attribution requires a fitted model. Construct "
                "XAIInterface(model=..., feature_names=...) or use "
                "trix.empirical.explain.compute_shap."
            )

        import numpy as np
        import shap

        names = self.feature_names or [
            k for k, v in input_data.items() if isinstance(v, (int, float))
        ]
        x = np.array([[float(input_data[n]) for n in names]], dtype=float)
        explainer = shap.TreeExplainer(self.model)
        values = explainer.shap_values(x)
        arr = np.asarray(values)
        if arr.ndim == 3:
            inst = np.mean(np.abs(arr[0]), axis=1)
        elif isinstance(values, list):
            inst = np.mean([np.abs(np.asarray(v)[0]) for v in values], axis=0)
        else:
            inst = np.abs(arr[0])
        inst = np.asarray(inst).ravel()[: len(names)]
        importance = {names[i]: float(inst[i]) for i in range(len(names))}

        return Explanation(
            method=ExplanationMethod.SHAP,
            feature_importance=dict(
                sorted(importance.items(), key=lambda kv: kv[1], reverse=True)
            ),
            rules=[],
            confidence=0.0,
            metadata={"explainer": "shap.TreeExplainer"},
        )

    def _explain_lime(self, input_data: Dict[str, Any]) -> Explanation:
        """LIME-based explanation.

        Delegates to the genuine local-surrogate implementation in
        ``trix.empirical.explain.compute_lime`` when a fitted model is attached.
        """
        if self.model is None:
            raise ValueError(
                "Genuine LIME attribution requires a fitted model. See "
                "trix.empirical.explain.compute_lime."
            )

        import numpy as np
        from trix.empirical.explain import compute_lime

        names = self.feature_names or [
            k for k, v in input_data.items() if isinstance(v, (int, float))
        ]
        x = np.array([float(input_data[n]) for n in names], dtype=float)
        background = (
            np.asarray(self.background, dtype=float)
            if self.background is not None
            else x.reshape(1, -1)
        )
        result = compute_lime(
            self.model.predict_proba, background, x, names,
            class_names=[str(c) for c in getattr(self.model, "classes_", [])],
        )
        importance = {f: abs(w) for f, w in result.get("local_weights", [])}

        return Explanation(
            method=ExplanationMethod.LIME,
            feature_importance=importance,
            rules=[],
            confidence=0.0,
            metadata={"explainer": result.get("method")},
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
