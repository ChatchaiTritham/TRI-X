"""Rule-based clinical baseline (the B1 baseline in the manuscript).

This is a deterministic, transparent forward-chaining classifier over the
TiTrATE / HINTS-style features produced by :mod:`trix.empirical.cohort`. It encodes
clinical decision logic directly (no training) and emits both a multiclass diagnosis
and a binary central/dangerous flag, so it can be compared head-to-head with the ML
ensemble on identical synthetic test cases.

The thresholds reuse the spirit of the repository's existing risk-governance layer
(:class:`trix.triage.TriageModule` / :class:`trix.governance.SRGL`): a case whose
gestalt risk and dangerous-HINTS findings exceed conservative thresholds is escalated
as central/dangerous.
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np

from .cohort import FEATURE_NAMES


class RuleBasedTriage:
    """Forward-chaining rule baseline over HINTS / TiTrATE features."""

    def __init__(self) -> None:
        self._idx: Dict[str, int] = {name: i for i, name in enumerate(FEATURE_NAMES)}

    def _f(self, row: np.ndarray, name: str) -> float:
        return float(row[self._idx[name]])

    def _central_score(self, row: np.ndarray) -> float:
        """Weighted dangerous-HINTS / vascular-risk score in [0, 1]-ish range."""
        score = 0.0
        # Dangerous HINTS triad (INFARCT mnemonic): normal HI, direction-changing or
        # vertical nystagmus, skew deviation -- each a central red flag.
        score += 0.30 * self._f(row, "head_impulse_normal")
        score += 0.22 * self._f(row, "nystagmus_direction_changing")
        score += 0.22 * self._f(row, "nystagmus_vertical")
        score += 0.25 * self._f(row, "skew_deviation")
        # Focal neurology and severe gait instability.
        score += 0.35 * self._f(row, "focal_neuro_deficit")
        score += 0.12 * self._f(row, "gait_unsteady_severe")
        # Vascular risk context.
        score += 0.05 * self._f(row, "n_vascular_risk_factors")
        score += 0.08 * self._f(row, "prior_stroke")
        # Acute continuous onset.
        score += 0.06 * (self._f(row, "onset_acute") * self._f(row, "continuous_symptoms"))
        return score

    def predict_central(self, X: np.ndarray) -> np.ndarray:
        """Binary central/dangerous prediction. Conservative threshold (high sensitivity)."""
        out = np.zeros(X.shape[0], dtype=int)
        for i in range(X.shape[0]):
            out[i] = 1 if self._central_score(X[i]) >= 0.30 else 0
        return out

    def predict_proba_central(self, X: np.ndarray) -> np.ndarray:
        """Pseudo-probability (squashed rule score) for the central class."""
        scores = np.array([self._central_score(X[i]) for i in range(X.shape[0])])
        return 1.0 / (1.0 + np.exp(-4.0 * (scores - 0.30)))

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Multiclass diagnosis via clinical pattern matching.

        Returns indices aligned with :data:`trix.empirical.cohort.DIAGNOSES`.
        """
        from .cohort import DIAGNOSES

        name_to_idx = {n: i for i, n in enumerate(DIAGNOSES)}
        preds: List[int] = []
        for i in range(X.shape[0]):
            row = X[i]
            if self._central_score(row) >= 0.30:
                # Decide which central pattern.
                if self._f(row, "episode_duration_min") < 120 and self._f(row, "focal_neuro_deficit") < 0.5:
                    dx = "TIA"
                elif self._f(row, "skew_deviation") > 0.5 and self._f(row, "gait_unsteady_severe") > 0.5:
                    dx = "Cerebellar Hemorrhage"
                else:
                    dx = "Posterior Circulation Stroke"
            else:
                # Benign peripheral pattern matching.
                if self._f(row, "positional_trigger") > 0.5 and self._f(row, "episode_duration_min") < 5:
                    dx = "BPPV"
                elif self._f(row, "hearing_loss") > 0.5 and self._f(row, "tinnitus") > 0.5:
                    dx = "Meniere's Disease" if self._f(row, "continuous_symptoms") < 0.5 else "Labyrinthitis"
                elif self._f(row, "headache") > 0.5 and self._f(row, "onset_acute") < 0.5:
                    dx = "Vestibular Migraine"
                elif self._f(row, "continuous_symptoms") > 0.5 and self._f(row, "onset_acute") > 0.5:
                    dx = "Vestibular Neuritis"
                elif self._f(row, "continuous_symptoms") > 0.5:
                    dx = "PPPD"
                else:
                    dx = "Benign Other"
            preds.append(name_to_idx[dx])
        return np.asarray(preds, dtype=int)
