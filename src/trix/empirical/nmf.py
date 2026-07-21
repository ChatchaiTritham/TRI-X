"""Data-level symptom-pattern factorization via Non-negative Matrix Factorization (NMF).

This module realises the *data-level* arm of TRI-X's XAI-by-design principle. Where
SHAP / LIME / DiCE explain a fitted model *post hoc* (output level), NMF operates on
the synthetic cohort feature matrix itself to recover latent **symptom-pattern factors**
-- additive, parts-based components that summarise how vestibular presentations cluster
into reusable structure before any predictive model is trained.

Because the synthetic cohort is generated from documented, archetype-conditioned
distributions (``trix.empirical.cohort``), the recovered factors can be read against the
known diagnostic archetypes: each factor's dominant samples concentrate on a small set
of archetypes, which is the transparency property the manuscript claims for NMF.

Determinism
-----------
NMF input is each feature min-max scaled to ``[0, 1]`` (NMF requires non-negativity).
With the ``nndsvda`` initialiser and a fixed ``random_state`` (default 42), the
factorization -- and therefore ``nmf_factors.json`` -- reproduces byte-for-byte.

DATA DISCLOSURE: operates only on the synthetic cohort. No real patient data is used.
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional

import numpy as np


def _scale_nonneg(X: np.ndarray) -> np.ndarray:
    """Per-feature min-max scale to ``[0, 1]`` so the matrix is non-negative for NMF."""
    X = np.asarray(X, dtype=float)
    mn = X.min(axis=0)
    mx = X.max(axis=0)
    span = np.where(mx > mn, mx - mn, 1.0)
    return (X - mn) / span


def factorize_symptoms(
    X: np.ndarray,
    feature_names: List[str],
    diagnosis_labels: Optional[np.ndarray] = None,
    diagnosis_names: Optional[List[str]] = None,
    n_components: int = 6,
    seed: int = 42,
    max_iter: int = 1000,
    top_features: int = 8,
) -> Dict[str, object]:
    """Factor the (scaled) symptom matrix into ``n_components`` non-negative factors.

    Parameters
    ----------
    X : np.ndarray
        ``(n, n_features)`` cohort feature matrix.
    feature_names : list of str
        Column names for ``X``.
    diagnosis_labels, diagnosis_names : optional
        If provided, each factor is annotated with the archetype distribution of the
        samples for which that factor is dominant (largest loading), linking latent
        structure back to known clinical archetypes.
    n_components : int
        Number of latent symptom-pattern factors.
    seed : int
        RNG seed for the NMF solver (default 42) -- fixes the output.

    Returns
    -------
    dict
        Availability flag, solver metadata, reconstruction error, and per-factor top
        features (+ archetype concentration when labels are supplied). Degrades
        gracefully to ``{"available": False}`` if scikit-learn is unavailable.
    """
    try:
        from sklearn.decomposition import NMF
    except Exception:  # pragma: no cover
        return {"available": False, "method": "sklearn NMF (not installed)"}

    Xs = _scale_nonneg(X)
    model = NMF(
        n_components=n_components,
        init="nndsvda",
        random_state=seed,
        max_iter=max_iter,
        tol=1e-4,
    )
    W = model.fit_transform(Xs)   # (n, k) sample loadings
    H = model.components_          # (k, n_features) factor-feature weights

    dominant = np.argmax(W, axis=1) if W.shape[0] else np.array([], dtype=int)

    factors: List[Dict[str, object]] = []
    for k in range(n_components):
        row = H[k]
        order = np.argsort(row)[::-1][:top_features]
        factor: Dict[str, object] = {
            "factor": k,
            "top_features": [(feature_names[j], round(float(row[j]), 6)) for j in order],
        }
        if diagnosis_labels is not None and diagnosis_names is not None:
            mask = dominant == k
            total = int(mask.sum())
            factor["n_dominant_samples"] = total
            if total:
                counts = Counter(int(v) for v in np.asarray(diagnosis_labels)[mask])
                arche = sorted(
                    (
                        (diagnosis_names[i], c, round(100.0 * c / total, 2))
                        for i, c in counts.items()
                    ),
                    key=lambda t: -t[1],
                )[:3]
                factor["top_archetypes"] = arche
        factors.append(factor)

    return {
        "available": True,
        "method": "sklearn.decomposition.NMF (nndsvda init; per-feature min-max scaled)",
        "n_components": int(n_components),
        "seed": int(seed),
        "n_samples": int(X.shape[0]),
        "n_features": int(X.shape[1]),
        "feature_scaling": "per-feature min-max to [0,1]",
        "reconstruction_err": round(float(model.reconstruction_err_), 6),
        "n_iter": int(model.n_iter_),
        "factors": factors,
    }
