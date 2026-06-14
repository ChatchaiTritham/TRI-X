"""Real machine-learning ensemble for TRI-X.

Implements the manuscript's ensemble: a soft-voting combination of

* Random Forest (sklearn),
* Gradient Boosting -- XGBoost if installed, otherwise sklearn GradientBoosting
  (the run reports which was actually used), and
* a small Multi-Layer Perceptron (sklearn ``MLPClassifier``).

All models are trained on the synthetic cohort with a fixed random seed so results
are deterministic. The single strongest component model is also exposed for the
"standalone ML" baseline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

try:  # XGBoost is optional; fall back to sklearn GradientBoosting if missing.
    from xgboost import XGBClassifier  # type: ignore

    _HAS_XGBOOST = True
except Exception:  # pragma: no cover - environment dependent
    _HAS_XGBOOST = False


@dataclass
class EnsembleInfo:
    """Records what was actually built (for honest reporting)."""

    gradient_model: str = "GradientBoosting"
    has_xgboost: bool = _HAS_XGBOOST
    component_names: List[str] = field(default_factory=list)


class TRIXEnsemble:
    """Soft-voting ensemble of RF + (XGBoost|GradientBoosting) + MLP."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.info = EnsembleInfo()
        self.classes_: Optional[np.ndarray] = None

        self.rf = RandomForestClassifier(
            n_estimators=400,
            max_depth=14,
            min_samples_leaf=2,
            random_state=seed,
            n_jobs=1,
            class_weight="balanced_subsample",
        )

        if _HAS_XGBOOST:
            self.gb = XGBClassifier(
                n_estimators=300,
                max_depth=5,
                learning_rate=0.08,
                subsample=0.9,
                colsample_bytree=0.9,
                random_state=seed,
                n_jobs=1,
                eval_metric="mlogloss",
                tree_method="hist",
            )
            self.info.gradient_model = "XGBoost"
        else:  # pragma: no cover - environment dependent
            self.gb = GradientBoostingClassifier(
                n_estimators=300,
                max_depth=3,
                learning_rate=0.08,
                subsample=0.9,
                random_state=seed,
            )
            self.info.gradient_model = "GradientBoosting"

        self.mlp = Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "mlp",
                    MLPClassifier(
                        hidden_layer_sizes=(128, 64, 32),
                        activation="relu",
                        alpha=1e-3,
                        max_iter=600,
                        early_stopping=True,
                        n_iter_no_change=20,
                        random_state=seed,
                    ),
                ),
            ]
        )

        self.info.component_names = [
            "RandomForest",
            self.info.gradient_model,
            "MLP",
        ]
        self._weights = np.array([0.4, 0.4, 0.2])  # RF, GB, MLP

        # Dedicated binary central/dangerous safety detector (the manuscript's
        # "multi-engine consensus algorithm for critical stroke/TIA detection").
        # A focused binary head is more sensitive on the high-stakes task than
        # collapsing an 11-way multiclass argmax.
        self.central_rf = RandomForestClassifier(
            n_estimators=400,
            max_depth=12,
            min_samples_leaf=2,
            random_state=seed,
            n_jobs=1,
            class_weight={0: 1.0, 1: 4.0},  # cost-sensitive: missing a stroke is catastrophic
        )
        self.central_threshold = 0.30  # conservative operating point (favour sensitivity)

    def fit(self, X: np.ndarray, y: np.ndarray, y_central: Optional[np.ndarray] = None) -> "TRIXEnsemble":
        self.rf.fit(X, y)
        self.gb.fit(X, y)
        self.mlp.fit(X, y)
        # Use the RF class order as canonical (sklearn estimators sort classes the same way).
        self.classes_ = self.rf.classes_
        if y_central is not None:
            self.central_rf.fit(X, y_central)
        return self

    def _aligned_proba(self, estimator, X: np.ndarray) -> np.ndarray:
        """Return probabilities aligned to ``self.classes_`` column order."""
        proba = estimator.predict_proba(X)
        est_classes = getattr(estimator, "classes_", None)
        if est_classes is None and hasattr(estimator, "named_steps"):
            est_classes = estimator.named_steps["mlp"].classes_
        if est_classes is None or np.array_equal(est_classes, self.classes_):
            return proba
        aligned = np.zeros((X.shape[0], len(self.classes_)))
        col = {c: j for j, c in enumerate(est_classes)}
        for j, c in enumerate(self.classes_):
            if c in col:
                aligned[:, j] = proba[:, col[c]]
        return aligned

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        p_rf = self._aligned_proba(self.rf, X)
        p_gb = self._aligned_proba(self.gb, X)
        p_mlp = self._aligned_proba(self.mlp, X)
        w = self._weights / self._weights.sum()
        return w[0] * p_rf + w[1] * p_gb + w[2] * p_mlp

    def predict(self, X: np.ndarray) -> np.ndarray:
        proba = self.predict_proba(X)
        return self.classes_[np.argmax(proba, axis=1)]

    def predict_proba_central(self, X: np.ndarray) -> np.ndarray:
        """Probability of the central/dangerous class from the dedicated binary head."""
        return self.central_rf.predict_proba(X)[:, 1]

    def predict_central(self, X: np.ndarray) -> np.ndarray:
        """Binary central/dangerous decision at the conservative operating threshold."""
        return (self.predict_proba_central(X) >= self.central_threshold).astype(int)

    # --- standalone single-model baseline (strongest component: RF) ---
    def standalone_predict(self, X: np.ndarray) -> np.ndarray:
        return self.rf.predict(X)

    def standalone_predict_central(self, X: np.ndarray, central_class_indices: List[int]) -> np.ndarray:
        """Central decision for the standalone single-model baseline (multiclass argmax)."""
        preds = self.rf.predict(X)
        cset = set(central_class_indices)
        return np.array([1 if int(p) in cset else 0 for p in preds], dtype=int)
