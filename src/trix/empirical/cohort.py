"""Synthetic emergency-department vestibular triage cohort generator.

This module generates a fully synthetic, clinically motivated cohort of emergency
department (ED) patients presenting with vestibular chief complaints. Every record
is drawn from documented, archetype-conditioned feature distributions; no real
patient data is used.

The generator is deterministic given a seed (default 42), so the cohort -- and every
downstream metric -- reproduces byte-for-byte across runs.

Clinical framing
----------------
Each synthetic patient is assigned one of several vestibular diagnostic archetypes.
Archetypes are grouped into:

* Peripheral / benign (BPPV, vestibular neuritis, labyrinthitis, Meniere's disease,
  vestibular migraine, PPPD, vestibular paroxysmia, and miscellaneous benign causes).
* Central / dangerous (posterior-circulation stroke, TIA, cerebellar hemorrhage).

The binary safety label used for the critical-scenario analysis is
``is_central`` (central/dangerous = 1, benign peripheral = 0).

Features are organized after the TiTrATE / HINTS clinical reasoning framework:
demographics and vascular risk, symptom timing/triggers, associated symptoms, and
the HINTS oculomotor examination. Distributions are conditioned on the archetype so
that, e.g., a central-stroke archetype is more likely to show a normal head-impulse
test, direction-changing/vertical nystagmus, and skew deviation -- the classic
"dangerous HINTS" pattern -- whereas BPPV is more likely to show short, positional,
trigger-provoked episodes.

The distributions below are illustrative clinical priors chosen to produce a learnable
but non-trivial classification problem; they are NOT claimed to be epidemiologically
exact and are disclosed as synthetic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Diagnostic archetypes
# ---------------------------------------------------------------------------

# name -> (group, base prevalence weight)
DIAGNOSES: Tuple[str, ...] = (
    "BPPV",
    "Vestibular Neuritis",
    "Labyrinthitis",
    "Meniere's Disease",
    "Vestibular Migraine",
    "PPPD",
    "Vestibular Paroxysmia",
    "Benign Other",
    "Posterior Circulation Stroke",
    "TIA",
    "Cerebellar Hemorrhage",
)

CENTRAL_DANGEROUS: Tuple[str, ...] = (
    "Posterior Circulation Stroke",
    "TIA",
    "Cerebellar Hemorrhage",
)

# Enriched prevalence weights (central conditions deliberately enriched relative to
# natural ED prevalence to support sensitivity learning for the high-stakes task).
_PREVALENCE: Dict[str, float] = {
    "BPPV": 0.255,
    "Vestibular Neuritis": 0.135,
    "Labyrinthitis": 0.085,
    "Meniere's Disease": 0.065,
    "Vestibular Migraine": 0.115,
    "PPPD": 0.060,
    "Vestibular Paroxysmia": 0.025,
    "Benign Other": 0.055,
    "Posterior Circulation Stroke": 0.095,
    "TIA": 0.045,
    "Cerebellar Hemorrhage": 0.010,
}

# ---------------------------------------------------------------------------
# Feature schema
# ---------------------------------------------------------------------------

FEATURE_NAMES: Tuple[str, ...] = (
    # demographics / vascular risk
    "age",
    "sex_female",
    "n_vascular_risk_factors",
    "hypertension",
    "diabetes",
    "smoking",
    "prior_stroke",
    # timing / triggers
    "onset_acute",            # 1 = sudden/acute, 0 = gradual/episodic
    "episode_duration_min",   # typical episode length in minutes (capped)
    "positional_trigger",
    "continuous_symptoms",
    # associated symptoms
    "hearing_loss",
    "tinnitus",
    "headache",
    "nausea_vomiting",
    "focal_neuro_deficit",
    # HINTS oculomotor exam (the dangerous-HINTS pattern flags central)
    "head_impulse_normal",    # normal HI is paradoxically a central red flag
    "nystagmus_vertical",
    "nystagmus_direction_changing",
    "skew_deviation",
    "gait_unsteady_severe",
    # gestalt risk score proxy
    "triage_risk_score",
)

N_FEATURES = len(FEATURE_NAMES)


@dataclass
class CohortArrays:
    """Container for a generated cohort."""

    X: np.ndarray              # (n, n_features) float
    y: np.ndarray              # (n,) int multiclass diagnosis index
    y_central: np.ndarray      # (n,) int binary central/dangerous label
    diagnosis_names: List[str]
    feature_names: List[str]


def _draw_patient(rng: np.random.Generator, dx: str) -> Dict[str, float]:
    """Draw one synthetic patient's features conditioned on the diagnosis archetype."""
    central = dx in CENTRAL_DANGEROUS

    # --- demographics / vascular risk ---
    if central:
        age = rng.normal(66.0, 12.0)
    elif dx in ("Vestibular Migraine", "PPPD"):
        age = rng.normal(43.0, 13.0)
    elif dx == "BPPV":
        age = rng.normal(56.0, 15.0)
    else:
        age = rng.normal(52.0, 16.0)
    age = float(np.clip(age, 18, 95))

    sex_female = float(rng.random() < (0.62 if dx in ("Vestibular Migraine", "Meniere's Disease") else 0.50))

    p_risk = 0.70 if central else 0.32
    hypertension = float(rng.random() < (0.75 if central else 0.30))
    diabetes = float(rng.random() < (0.45 if central else 0.16))
    smoking = float(rng.random() < (0.40 if central else 0.20))
    prior_stroke = float(rng.random() < (0.22 if central else 0.03))
    n_vascular = hypertension + diabetes + smoking + prior_stroke + float(rng.random() < p_risk * 0.3)

    # --- timing / triggers ---
    if dx == "BPPV":
        onset_acute = float(rng.random() < 0.30)
        episode_duration = float(np.clip(rng.exponential(0.7), 0.05, 5.0))   # seconds-minutes
        positional_trigger = float(rng.random() < 0.88)
        continuous = float(rng.random() < 0.05)
    elif dx in ("Vestibular Neuritis", "Labyrinthitis"):
        onset_acute = float(rng.random() < 0.85)
        episode_duration = float(np.clip(rng.normal(2880, 600), 60, 4320))   # days -> minutes (continuous)
        positional_trigger = float(rng.random() < 0.20)
        continuous = float(rng.random() < 0.85)
    elif dx == "Meniere's Disease":
        onset_acute = float(rng.random() < 0.55)
        episode_duration = float(np.clip(rng.normal(120, 60), 20, 720))
        positional_trigger = float(rng.random() < 0.15)
        continuous = float(rng.random() < 0.25)
    elif dx == "Vestibular Migraine":
        onset_acute = float(rng.random() < 0.45)
        episode_duration = float(np.clip(rng.normal(300, 200), 5, 4320))
        positional_trigger = float(rng.random() < 0.30)
        continuous = float(rng.random() < 0.30)
    elif dx == "PPPD":
        onset_acute = float(rng.random() < 0.20)
        episode_duration = float(np.clip(rng.normal(1440, 700), 60, 4320))
        positional_trigger = float(rng.random() < 0.40)
        continuous = float(rng.random() < 0.70)
    elif dx == "Vestibular Paroxysmia":
        onset_acute = float(rng.random() < 0.50)
        episode_duration = float(np.clip(rng.exponential(0.5), 0.02, 3.0))
        positional_trigger = float(rng.random() < 0.35)
        continuous = float(rng.random() < 0.05)
    elif central:
        onset_acute = float(rng.random() < 0.90)
        if dx == "TIA":
            episode_duration = float(np.clip(rng.normal(30, 25), 2, 720))
            continuous = float(rng.random() < 0.30)
        else:
            episode_duration = float(np.clip(rng.normal(2880, 800), 120, 4320))
            continuous = float(rng.random() < 0.88)
        positional_trigger = float(rng.random() < 0.12)
    else:  # Benign Other
        onset_acute = float(rng.random() < 0.40)
        episode_duration = float(np.clip(rng.normal(200, 200), 1, 4320))
        positional_trigger = float(rng.random() < 0.30)
        continuous = float(rng.random() < 0.30)

    # --- associated symptoms ---
    hearing_loss = float(rng.random() < (0.55 if dx in ("Labyrinthitis", "Meniere's Disease") else (0.05 if central else 0.10)))
    tinnitus = float(rng.random() < (0.50 if dx in ("Meniere's Disease", "Labyrinthitis") else 0.12))
    headache = float(rng.random() < (0.60 if dx == "Vestibular Migraine" else (0.55 if central else 0.15)))
    nausea_vomiting = float(rng.random() < (0.70 if dx in ("Vestibular Neuritis", "Labyrinthitis") or central else 0.40))
    focal_neuro = float(rng.random() < (0.55 if central else 0.02))

    # --- HINTS oculomotor exam ---
    if central:
        head_impulse_normal = float(rng.random() < 0.78)             # central red flag
        nystagmus_vertical = float(rng.random() < 0.45)
        nystagmus_dir_changing = float(rng.random() < 0.50)
        skew_deviation = float(rng.random() < 0.40)
        gait_severe = float(rng.random() < 0.55)
    elif dx in ("Vestibular Neuritis", "Labyrinthitis"):
        head_impulse_normal = float(rng.random() < 0.15)             # abnormal HI = peripheral
        nystagmus_vertical = float(rng.random() < 0.04)
        nystagmus_dir_changing = float(rng.random() < 0.05)
        skew_deviation = float(rng.random() < 0.04)
        gait_severe = float(rng.random() < 0.20)
    else:
        head_impulse_normal = float(rng.random() < 0.55)
        nystagmus_vertical = float(rng.random() < 0.05)
        nystagmus_dir_changing = float(rng.random() < 0.08)
        skew_deviation = float(rng.random() < 0.05)
        gait_severe = float(rng.random() < 0.10)

    # --- gestalt triage risk-score proxy (0-1), correlated with danger ---
    base = 0.25
    base += 0.18 * focal_neuro + 0.12 * skew_deviation + 0.10 * nystagmus_vertical
    base += 0.08 * head_impulse_normal + 0.07 * nystagmus_dir_changing
    base += 0.05 * (n_vascular / 4.0) + 0.06 * gait_severe + 0.04 * onset_acute
    base += float(rng.normal(0.0, 0.06))
    triage_risk = float(np.clip(base, 0.0, 1.0))

    return {
        "age": age,
        "sex_female": sex_female,
        "n_vascular_risk_factors": float(np.clip(n_vascular, 0, 5)),
        "hypertension": hypertension,
        "diabetes": diabetes,
        "smoking": smoking,
        "prior_stroke": prior_stroke,
        "onset_acute": onset_acute,
        "episode_duration_min": episode_duration,
        "positional_trigger": positional_trigger,
        "continuous_symptoms": continuous,
        "hearing_loss": hearing_loss,
        "tinnitus": tinnitus,
        "headache": headache,
        "nausea_vomiting": nausea_vomiting,
        "focal_neuro_deficit": focal_neuro,
        "head_impulse_normal": head_impulse_normal,
        "nystagmus_vertical": nystagmus_vertical,
        "nystagmus_direction_changing": nystagmus_dir_changing,
        "skew_deviation": skew_deviation,
        "gait_unsteady_severe": gait_severe,
        "triage_risk_score": triage_risk,
    }


def generate_cohort(n: int = 5000, seed: int = 42) -> CohortArrays:
    """Generate a deterministic synthetic ED vestibular triage cohort.

    Parameters
    ----------
    n : int
        Number of synthetic patients.
    seed : int
        RNG seed (default 42) -- fixes the cohort and all downstream metrics.
    """
    rng = np.random.default_rng(seed)
    names = list(DIAGNOSES)
    weights = np.array([_PREVALENCE[d] for d in names], dtype=float)
    weights = weights / weights.sum()

    dx_indices = rng.choice(len(names), size=n, p=weights)

    rows: List[List[float]] = []
    y_central: List[int] = []
    for idx in dx_indices:
        dx = names[idx]
        feats = _draw_patient(rng, dx)
        rows.append([feats[f] for f in FEATURE_NAMES])
        y_central.append(1 if dx in CENTRAL_DANGEROUS else 0)

    X = np.asarray(rows, dtype=float)
    y = np.asarray(dx_indices, dtype=int)
    return CohortArrays(
        X=X,
        y=y,
        y_central=np.asarray(y_central, dtype=int),
        diagnosis_names=names,
        feature_names=list(FEATURE_NAMES),
    )
