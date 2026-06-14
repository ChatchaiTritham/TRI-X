"""Genuine post-hoc explainability over the fitted TRI-X models.

Replaces the package's earlier placeholder explanation logic with real attributions
computed from the trained models:

* ``compute_shap`` -- SHAP values via :class:`shap.TreeExplainer` on the Random Forest
  component (exact tree-path attributions, not a normalized-input heuristic).
* ``compute_lime`` -- a local linear surrogate via the ``lime`` tabular explainer for a
  single instance (only if ``lime`` is installed).
* ``compute_dice`` -- diverse counterfactuals via ``dice-ml`` for a single instance
  (only if ``dice-ml`` is installed).

Each helper degrades gracefully and reports availability, so the pipeline can honestly
state which explainers were actually exercised.
"""

from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np


def compute_shap(rf_model, X_background: np.ndarray, X_explain: np.ndarray,
                 feature_names: List[str]) -> Dict[str, object]:
    """Mean |SHAP| global feature importance from the Random Forest.

    Returns a dict with availability flag, per-feature mean-absolute SHAP importance
    (ranked), and the number of instances explained.
    """
    import shap

    explainer = shap.TreeExplainer(rf_model)
    shap_values = explainer.shap_values(X_explain)

    # shap_values may be a list (per class) or a 3D array (n, features, classes).
    arr = np.asarray(shap_values)
    if arr.ndim == 3:
        # (n, features, classes) -> mean over instances and classes of |value|
        mean_abs = np.mean(np.abs(arr), axis=(0, 2))
    elif isinstance(shap_values, list):
        stacked = np.stack([np.abs(np.asarray(s)) for s in shap_values], axis=0)
        mean_abs = stacked.mean(axis=(0, 1))
    else:
        mean_abs = np.mean(np.abs(arr), axis=0)

    mean_abs = np.asarray(mean_abs).ravel()[: len(feature_names)]
    importance = {feature_names[i]: float(mean_abs[i]) for i in range(len(feature_names))}
    ranked = dict(sorted(importance.items(), key=lambda kv: kv[1], reverse=True))
    return {
        "available": True,
        "method": "shap.TreeExplainer(RandomForest)",
        "n_explained": int(X_explain.shape[0]),
        "global_importance": ranked,
        "top10": list(ranked.items())[:10],
    }


def compute_lime(predict_proba_fn, X_train: np.ndarray, x_instance: np.ndarray,
                 feature_names: List[str], class_names: List[str],
                 seed: int = 42) -> Dict[str, object]:
    """Local LIME explanation for one instance (if ``lime`` available)."""
    try:
        from lime.lime_tabular import LimeTabularExplainer
    except Exception:  # pragma: no cover
        return {"available": False, "method": "lime (not installed)"}

    explainer = LimeTabularExplainer(
        training_data=X_train,
        feature_names=feature_names,
        class_names=class_names,
        discretize_continuous=True,
        random_state=seed,
        mode="classification",
    )
    pred = int(np.argmax(predict_proba_fn(x_instance.reshape(1, -1))[0]))
    exp = explainer.explain_instance(
        x_instance,
        predict_proba_fn,
        num_features=min(10, len(feature_names)),
        labels=(pred,),
    )
    weights = exp.as_list(label=pred)
    return {
        "available": True,
        "method": "lime.LimeTabularExplainer (local linear surrogate)",
        "explained_class": class_names[pred] if pred < len(class_names) else str(pred),
        "local_weights": [(str(f), float(w)) for f, w in weights],
    }


def compute_dice(ensemble, X_train: np.ndarray, y_train: np.ndarray,
                 x_instance: np.ndarray, feature_names: List[str],
                 class_names: List[str]) -> Dict[str, object]:
    """Diverse counterfactual explanation for one instance (if ``dice-ml`` available)."""
    try:
        import dice_ml
        import pandas as pd
    except Exception:  # pragma: no cover
        return {"available": False, "method": "dice-ml (not installed)"}

    try:
        df = pd.DataFrame(X_train, columns=feature_names)
        df["target"] = y_train
        d = dice_ml.Data(
            dataframe=df,
            continuous_features=feature_names,
            outcome_name="target",
        )

        class _Wrapper:
            def __init__(self, model):
                self.model = model

            def predict_proba(self, X):
                if hasattr(X, "values"):
                    X = X.values
                return self.model.predict_proba(np.asarray(X, dtype=float))

            def predict(self, X):
                if hasattr(X, "values"):
                    X = X.values
                return self.model.predict(np.asarray(X, dtype=float))

        m = dice_ml.Model(model=_Wrapper(ensemble), backend="sklearn", model_type="classifier")
        exp = dice_ml.Dice(d, m, method="random")
        query = pd.DataFrame(x_instance.reshape(1, -1), columns=feature_names)
        orig = int(ensemble.predict(x_instance.reshape(1, -1))[0])
        # Counterfactual toward any different class.
        desired = [c for c in np.unique(y_train) if c != orig][:1]
        cf = exp.generate_counterfactuals(
            query, total_CFs=2, desired_class=int(desired[0])
        )
        cf_df = cf.cf_examples_list[0].final_cfs_df
        return {
            "available": True,
            "method": "dice-ml (diverse counterfactual explanations)",
            "original_class": class_names[orig] if orig < len(class_names) else str(orig),
            "n_counterfactuals": int(0 if cf_df is None else len(cf_df)),
        }
    except Exception as exc:  # pragma: no cover - DiCE can be finicky
        return {
            "available": True,
            "method": "dice-ml (installed; generation incomplete)",
            "note": f"counterfactual generation raised: {type(exc).__name__}",
        }
