"""
TRI-X Framework Demo Script.

Demonstrates basic usage of the TRI-X framework for emergency triage.
"""

import sys
from pathlib import Path

# Add parent directory to path for direct script execution.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from trix import (
    ExplanationMethod,
    ScreeningPolicy,
    SRGL,
    TiTrATEEngine,
    TriageModule,
    TRIXPipeline,
    XAIInterface,
)


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60)


def print_section(text):
    """Print a formatted section title."""
    print("\n" + "-" * 60)
    print(text)
    print("-" * 60)


def main():
    print_header("TRI-X FRAMEWORK DEMO")

    print_section("1. Initializing TRI-X Components")

    triage = TriageModule(
        threshold=0.7,
        feature_weights={
            "urgency": 2.0,
            "severity": 1.5,
            "complexity": 1.0,
        },
    )
    print("[OK] Triage Module initialized")

    titrate = TiTrATEEngine(max_time=5.0)
    print("[OK] TiTrATE Engine initialized")

    xai = XAIInterface(method=ExplanationMethod.SHAP)
    print("[OK] XAI Interface initialized")

    governance = SRGL(screening_policy=ScreeningPolicy.CONSERVATIVE)
    print("[OK] SRGL Governance initialized")

    pipeline = TRIXPipeline(triage, titrate, xai, governance)
    print("[OK] TRI-X Pipeline created")

    print_section("2. Processing Low-Risk Patient")

    low_risk_patient = {
        "features": {
            "urgency": 0.25,
            "severity": 0.20,
            "complexity": 0.15,
        },
        "metadata": {
            "patient_id": "PT-001",
            "chief_complaint": "minor_headache",
        },
    }

    result1 = pipeline.process(low_risk_patient)

    print(f"\nPatient ID: {low_risk_patient['metadata']['patient_id']}")
    print(f"Chief Complaint: {low_risk_patient['metadata']['chief_complaint']}")
    print("\nResults:")
    print(f" Risk Level: {result1.triage.risk_level.name}")
    print(f" Risk Score: {result1.triage.risk_score:.3f}")
    print(f" SRGL Approved: {result1.governance.approved}")
    print(f" Final Decision: {result1.final_decision}")

    print("\nTop Contributing Features:")
    for feature, importance in sorted(
        result1.explanation.feature_importance.items(),
        key=lambda x: x[1],
        reverse=True,
    )[:3]:
        print(f" - {feature}: {importance:.3f}")

    print_section("3. Processing High-Risk Patient")

    high_risk_patient = {
        "features": {
            "urgency": 0.95,
            "severity": 0.88,
            "complexity": 0.75,
        },
        "metadata": {
            "patient_id": "PT-002",
            "chief_complaint": "chest_pain_acute",
        },
    }

    result2 = pipeline.process(high_risk_patient)

    print(f"\nPatient ID: {high_risk_patient['metadata']['patient_id']}")
    print(f"Chief Complaint: {high_risk_patient['metadata']['chief_complaint']}")
    print("\nResults:")
    print(f" Risk Level: {result2.triage.risk_level.name}")
    print(f" Risk Score: {result2.triage.risk_score:.3f}")
    print(f" SRGL Approved: {result2.governance.approved}")
    print(f" Final Decision: {result2.final_decision}")

    print("\nTop Contributing Features:")
    for feature, importance in sorted(
        result2.explanation.feature_importance.items(),
        key=lambda x: x[1],
        reverse=True,
    )[:3]:
        print(f" - {feature}: {importance:.3f}")

    if result2.governance.violations:
        print("\nGovernance Violations:")
        for violation in result2.governance.violations:
            print(f" - {violation}")

    print_section("4. Summary")

    print("\nPipeline Statistics:")
    stats = pipeline.get_statistics()
    print(f" Governance Policy: {stats['governance']['policy']}")
    print(f" Governance Constraints: {len(stats['governance']['constraints'])}")

    print_header("DEMO COMPLETE")
    print("\nNext Steps:")
    print(" - Explore Jupyter notebooks in notebooks/")
    print(" - Read API documentation in docs/")
    print(" - Run validation: python scripts/run_validation.py")
    print(" - Check tests: pytest tests/")
    print()


if __name__ == "__main__":
    main()
