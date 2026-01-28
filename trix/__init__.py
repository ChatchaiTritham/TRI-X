"""
TRI-X: Triage-TiTrATE-XAI Framework
====================================

An integrated framework for safe AI decision-making in critical systems.
"""

__version__ = "0.1.0"
__author__ = "Your Name"

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
]
