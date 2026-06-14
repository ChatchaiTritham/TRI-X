"""Empirical pipeline for TRI-X.

This subpackage provides an honest, fully reproducible empirical pipeline for the
TRI-X expert system: a documented synthetic emergency-department vestibular triage
cohort generator, a clinical rule-based baseline scorer, a real machine-learning
ensemble (Random Forest + Gradient Boosting + Multi-Layer Perceptron), and genuine
post-hoc explainability (SHAP, and -- when available -- LIME and DiCE) computed from
the fitted models.

All data are SYNTHETIC and disclosed as such. No real patient records and no human
ratings are used anywhere in this pipeline.
"""

from .cohort import (
    DIAGNOSES,
    CENTRAL_DANGEROUS,
    FEATURE_NAMES,
    generate_cohort,
)
from .rule_baseline import RuleBasedTriage
from .ensemble import TRIXEnsemble

__all__ = [
    "DIAGNOSES",
    "CENTRAL_DANGEROUS",
    "FEATURE_NAMES",
    "generate_cohort",
    "RuleBasedTriage",
    "TRIXEnsemble",
]
