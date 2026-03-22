"""
TRI-X: Triage-TiTrATE-XAI Framework
====================================

An integrated framework for safe AI decision-making in critical systems.
"""

from .constants import FRAMEWORK_NAME, PACKAGE_VERSION

__version__ = PACKAGE_VERSION
__author__ = "Clinical AI Research Team"

from .triage import TriageModule, RiskLevel
from .titrate import TiTrATEEngine, TemporalConstraint
from .xai import XAIInterface, ExplanationMethod
from .governance import SRGL, ScreeningPolicy
from .pipeline import TRIXPipeline, TRIXResult

__all__ = [
    "TriageModule",
    "RiskLevel",
    "TiTrATEEngine",
    "TemporalConstraint",
    "XAIInterface",
    "ExplanationMethod",
    "SRGL",
    "ScreeningPolicy",
    "TRIXPipeline",
    "TRIXResult",
    "FRAMEWORK_NAME",
]
