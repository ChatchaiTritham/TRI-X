# TRI-X Development Plan
**Following BASICS-CDSS Methodology**

**Status:** Framework Skeleton → Production-Ready Implementation
**Timeline:** 3-6 months
**Approach:** Modular, Test-Driven, Manuscript-Aligned

---

## Executive Summary

Based on manuscript analysis and codebase review, TRI-X currently has **35-40% completeness**. This plan brings it to **90%+ research-ready** by implementing:

1. Clinical guideline integration (ACEP, AHA/ASA, AAO-HNS)
2. Real XAI (SHAP/LIME, not simulated)
3. Uncertainty quantification system
4. Complete TiTrATE trigger logic
5. G1-G5 clinical classification
6. Comprehensive testing (80%+ coverage)
7. Tutorial notebooks (00-06)

---

## Current Status (Detailed Analysis)

### ✅ What's Working (60-70% complete)
- ✓ Module structure (triage, titrate, xai, governance, pipeline)
- ✓ Pipeline orchestration
- ✓ Basic risk scoring
- ✓ Temporal execution with timeouts
- ✓ SRGL governance gates (4 gates)
- ✓ Documentation (README, QUICKSTART)

### ⚠️ What's Partial (20-50% complete)
- ⚠️ Triage: Generic scoring (no clinical guidelines)
- ⚠️ TiTrATE: Time-based only (no triggers)
- ⚠️ Governance: 4 gates (needs G1-G5 mapping)
- ⚠️ Testing: Only triage tested

### ❌ What's Missing (0-20% complete)
- ❌ XAI: **Simulated explanations** (critical gap!)
- ❌ Clinical guidelines: ACEP, AHA/ASA, AAO-HNS not encoded
- ❌ Uncertainty quantification: No system
- ❌ Trigger logic: TiTrATE missing "Triggers" component
- ❌ Validation: Claims unvalidated (98.7% sensitivity, etc.)

---

## Development Phases

### **Phase 1: Clinical Foundation (Weeks 1-4)**

#### 1.1 Clinical Guideline Modules

**Create:** `trix/clinical/`

```
trix/clinical/
├── __init__.py
├── guidelines.py          # Base guideline class
├── acep_dizziness.py      # ACEP dizziness/vertigo
├── aha_stroke.py          # AHA/ASA stroke guidelines
├── aaohns_bppv.py         # AAO-HNS BPPV guidelines
├── red_flags.py           # Red flag detection
└── risk_factors.py        # Risk factor scoring
```

**Implementation:**

```python
# trix/clinical/guidelines.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class GuidelineRecommendation:
    """Clinical guideline recommendation."""
    level: str  # G1-G5
    action: str
    rationale: str
    evidence_grade: str  # A, B, C
    references: List[str]

class ClinicalGuideline(ABC):
    """Base class for clinical guidelines."""

    @abstractmethod
    def evaluate(self, patient_data: Dict) -> GuidelineRecommendation:
        """Evaluate patient against guideline."""
        pass

    @abstractmethod
    def check_red_flags(self, patient_data: Dict) -> List[str]:
        """Check for red flags."""
        pass

# trix/clinical/acep_dizziness.py
class ACEPDizzinessGuideline(ClinicalGuideline):
    """
    ACEP Clinical Policy for Adult Acute Dizziness/Vertigo
    Based on GRACE-3 (2023)
    """

    RED_FLAGS = [
        "new_severe_headache",
        "neurologic_deficit",
        "unstable_vital_signs",
        "chest_pain",
        "severe_vomiting"
    ]

    def check_red_flags(self, patient_data: Dict) -> List[str]:
        """Check for life-threatening red flags."""
        flags = []
        symptoms = patient_data.get('symptoms', {})

        # Severe headache (thunderclap)
        if symptoms.get('headache_severity', 0) >= 8:
            flags.append("new_severe_headache")

        # Neurologic deficits
        if any(symptoms.get(deficit, False) for deficit in [
            'focal_weakness', 'speech_difficulty',
            'visual_loss', 'altered_consciousness'
        ]):
            flags.append("neurologic_deficit")

        # Vital sign instability
        vitals = patient_data.get('vitals', {})
        if (vitals.get('systolic_bp', 120) < 90 or
            vitals.get('systolic_bp', 120) > 180 or
            vitals.get('heart_rate', 70) < 50 or
            vitals.get('heart_rate', 70) > 120):
            flags.append("unstable_vital_signs")

        return flags

    def evaluate(self, patient_data: Dict) -> GuidelineRecommendation:
        """
        Evaluate according to ACEP/GRACE-3 guidelines.

        Mapping:
        - Any red flag → G1 (Immediate Emergency)
        - High-risk pattern → G2 (Urgent Specialist)
        - Moderate uncertainty → G3 (Early Follow-up)
        - Low-risk pattern → G4 (Routine Care)
        - Minimal risk → G5 (Reassurance)
        """
        # Check red flags first
        red_flags = self.check_red_flags(patient_data)
        if red_flags:
            return GuidelineRecommendation(
                level="G1",
                action="ER_IMMEDIATE",
                rationale=f"Red flags detected: {', '.join(red_flags)}",
                evidence_grade="A",
                references=["GRACE-3 2023", "ACEP Clinical Policy"]
            )

        # Assess risk pattern
        pattern = self._assess_pattern(patient_data)

        if pattern == "acute_vestibular_syndrome":
            # Check for central causes (HINTS exam)
            hints_positive = self._evaluate_hints(patient_data)
            if hints_positive:
                return GuidelineRecommendation(
                    level="G2",
                    action="NEURO_URGENT",
                    rationale="AVS with central pattern (HINTS+)",
                    evidence_grade="A",
                    references=["Kattah 2009 HINTS"]
                )

        # Continue with other patterns...
        return self._evaluate_by_pattern(pattern, patient_data)
```

#### 1.2 Red Flag Detection System

**Create:** `trix/clinical/red_flags.py`

```python
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class RedFlag:
    """Individual red flag."""
    flag_id: str
    severity: int  # 1-10
    category: str  # "neurologic", "cardiac", "vital_signs"
    description: str
    guideline_source: str

class RedFlagDetector:
    """Detects life-threatening red flags."""

    # Neurologic red flags (posterior stroke risk)
    NEUROLOGIC_FLAGS = {
        "new_severe_headache": RedFlag(
            "RF_NEURO_01",
            severity=9,
            category="neurologic",
            description="Sudden severe headache (thunderclap)",
            guideline_source="ACEP GRACE-3"
        ),
        "focal_weakness": RedFlag(
            "RF_NEURO_02",
            severity=10,
            category="neurologic",
            description="Unilateral weakness",
            guideline_source="AHA/ASA Stroke"
        ),
        # ... more flags
    }

    def detect_all(self, patient_data: Dict) -> Tuple[List[RedFlag], int]:
        """
        Detect all red flags in patient data.

        Returns:
            (list of detected flags, max severity)
        """
        detected = []

        # Check each category
        detected.extend(self._check_neurologic(patient_data))
        detected.extend(self._check_cardiac(patient_data))
        detected.extend(self._check_vital_signs(patient_data))

        max_severity = max([f.severity for f in detected], default=0)

        return detected, max_severity
```

#### 1.3 TiTrATE Pattern Matching

**Extend:** `trix/titrate.py`

```python
from enum import Enum
from typing import Dict, Optional

class TiTrATEPattern(Enum):
    """TiTrATE symptom patterns (Timing-Triggers-Targeted Examination)."""
    ACUTE_VESTIBULAR_SYNDROME = "AVS"  # Sudden, continuous days
    EPISODIC_VESTIBULAR_SYNDROME = "EVS"  # Recurrent episodes
    TRIGGERED_VESTIBULAR_SYNDROME = "TVS"  # Positional (BPPV)
    NON_SPECIFIC = "NS"
    UNKNOWN = "UNK"

class TiTrATEPatternMatcher:
    """
    Identifies clinical patterns using TiTrATE framework.

    Timing: Onset, duration, evolution
    Triggers: Positional, activity-related
    Targeted Examination: Nystagmus, gait, HINTS
    """

    def match_pattern(self, patient_data: Dict) -> TiTrATEPattern:
        """Match patient presentation to TiTrATE pattern."""

        timing = patient_data.get('timing', {})
        triggers = patient_data.get('triggers', {})
        exam = patient_data.get('examination', {})

        # 1. Check for positional triggers (TVS/BPPV)
        if triggers.get('positional', False):
            if exam.get('dix_hallpike_positive', False):
                return TiTrATEPattern.TRIGGERED_VESTIBULAR_SYNDROME

        # 2. Check timing for AVS
        onset = timing.get('onset', 'unknown')
        duration_hours = timing.get('duration_hours', 0)

        if onset == 'sudden' and duration_hours >= 24:
            # Acute Vestibular Syndrome
            return TiTrATEPattern.ACUTE_VESTIBULAR_SYNDROME

        # 3. Check for episodic pattern
        if timing.get('recurrent', False):
            episode_duration_minutes = timing.get('episode_duration_minutes', 0)
            if episode_duration_minutes < 60:
                return TiTrATEPattern.EPISODIC_VESTIBULAR_SYNDROME

        return TiTrATEPattern.NON_SPECIFIC
```

---

### **Phase 2: Real XAI Implementation (Weeks 5-8)**

#### 2.1 Replace Simulated XAI with Real Implementations

**Modify:** `trix/xai.py`

```python
import shap
import lime
import lime.lime_tabular
import numpy as np
from typing import Dict, Any

class XAIInterface:
    """Real XAI implementation (not simulated)."""

    def __init__(self, model=None):
        """
        Initialize XAI with actual model.

        Args:
            model: Trained model (sklearn, etc.)
        """
        self.model = model
        self.explainer_shap = None
        self.explainer_lime = None

    def _explain_shap_real(self, features: Dict[str, float],
                          background_data: np.ndarray) -> Dict[str, float]:
        """
        Real SHAP implementation.

        Args:
            features: Input features
            background_data: Background dataset for SHAP

        Returns:
            Feature importance from actual SHAP values
        """
        if self.model is None:
            raise ValueError("Model required for real SHAP")

        # Initialize SHAP explainer if not exists
        if self.explainer_shap is None:
            self.explainer_shap = shap.KernelExplainer(
                self.model.predict_proba,
                background_data
            )

        # Convert features to array
        feature_array = self._dict_to_array(features)

        # Compute SHAP values
        shap_values = self.explainer_shap.shap_values(feature_array)

        # Convert back to dict
        feature_names = list(features.keys())
        importance = {
            name: abs(float(shap_values[0][i]))
            for i, name in enumerate(feature_names)
        }

        return importance

    def _explain_lime_real(self, features: Dict[str, float],
                          training_data: np.ndarray,
                          training_labels: np.ndarray) -> Dict[str, float]:
        """
        Real LIME implementation.

        Args:
            features: Input features
            training_data: Training dataset
            training_labels: Training labels

        Returns:
            Feature importance from actual LIME
        """
        if self.model is None:
            raise ValueError("Model required for real LIME")

        # Initialize LIME explainer
        if self.explainer_lime is None:
            feature_names = list(features.keys())
            self.explainer_lime = lime.lime_tabular.LimeTabularExplainer(
                training_data,
                feature_names=feature_names,
                class_names=['low_risk', 'high_risk'],
                mode='classification'
            )

        # Convert features to array
        feature_array = self._dict_to_array(features)

        # Get explanation
        exp = self.explainer_lime.explain_instance(
            feature_array,
            self.model.predict_proba,
            num_features=len(features)
        )

        # Extract feature importance
        importance = {
            name: abs(weight)
            for name, weight in exp.as_list()
        }

        return importance

    def _dict_to_array(self, features: Dict[str, float]) -> np.ndarray:
        """Convert feature dict to numpy array."""
        return np.array([features[k] for k in sorted(features.keys())])
```

#### 2.2 XAI Fidelity Validation

**Create:** `trix/xai_validation.py`

```python
def compute_explanation_fidelity(
    model,
    explanation_method: str,
    test_data: np.ndarray,
    test_labels: np.ndarray
) -> float:
    """
    Compute explanation fidelity (agreement with model).

    Fidelity = how well explanation predicts model behavior

    Returns:
        Fidelity score (0-1, higher is better)
    """
    from sklearn.metrics import r2_score

    # Get model predictions
    model_predictions = model.predict_proba(test_data)[:, 1]

    # Get explanation-based predictions
    # (simplified linear model using feature importance)
    explanation_predictions = []

    for sample in test_data:
        # Get explanation for this sample
        importance = get_explanation(model, sample, explanation_method)

        # Weighted sum (simple approximation)
        pred = sum(sample[i] * importance[i] for i in range(len(sample)))
        explanation_predictions.append(pred)

    # Compute R² between model and explanation
    fidelity = r2_score(model_predictions, explanation_predictions)

    return fidelity
```

---

### **Phase 3: Uncertainty Quantification (Weeks 9-10)**

#### 3.1 Uncertainty System

**Create:** `trix/uncertainty.py`

```python
from dataclasses import dataclass
from typing import Dict, Tuple
import numpy as np

@dataclass
class UncertaintyProfile:
    """Uncertainty quantification for patient case."""
    information: float  # 0-1, data completeness
    diagnostic: float   # 0-1, diagnosis ambiguity
    policy: float       # 0-1, guideline ambiguity
    total: float        # Combined uncertainty
    sources: Dict[str, float]  # Detailed breakdown

class UncertaintyQuantifier:
    """
    Quantify uncertainty following manuscript equation:
    u(x) = u_info(x) + u_diag(x) + u_policy(x)
    """

    def quantify(self, patient_data: Dict) -> UncertaintyProfile:
        """
        Compute uncertainty profile.

        Returns:
            UncertaintyProfile with all components
        """
        u_info = self._information_uncertainty(patient_data)
        u_diag = self._diagnostic_uncertainty(patient_data)
        u_policy = self._policy_uncertainty(patient_data)

        # Total uncertainty (normalized)
        u_total = (u_info + u_diag + u_policy) / 3.0

        return UncertaintyProfile(
            information=u_info,
            diagnostic=u_diag,
            policy=u_policy,
            total=u_total,
            sources={
                'missing_fields': self._count_missing(patient_data),
                'ambiguous_symptoms': self._count_ambiguous(patient_data),
                'overlapping_diagnoses': self._count_overlapping(patient_data)
            }
        )

    def _information_uncertainty(self, patient_data: Dict) -> float:
        """
        u_info = 1 - (fields_present / total_required_fields)

        TiTrATE required fields:
        - Timing: onset, duration
        - Triggers: positional, activity
        - Targeted Exam: nystagmus, gait, HINTS
        """
        required_fields = [
            'timing.onset',
            'timing.duration_hours',
            'triggers.positional',
            'examination.nystagmus',
            'examination.gait'
        ]

        present = sum(
            1 for field in required_fields
            if self._field_exists(patient_data, field)
        )

        completeness = present / len(required_fields)
        uncertainty = 1.0 - completeness

        return uncertainty

    def _diagnostic_uncertainty(self, patient_data: Dict) -> float:
        """
        u_diag = count(plausible_diagnoses) / total_diagnoses

        Based on symptom overlap across conditions.
        """
        # Get plausible diagnoses from guideline matching
        plausible = self._get_plausible_diagnoses(patient_data)
        total_diagnoses = 50  # Total in dizziness/vertigo ontology

        uncertainty = len(plausible) / total_diagnoses

        return uncertainty

    def _policy_uncertainty(self, patient_data: Dict) -> float:
        """
        u_policy = presence of conflicting guidelines

        Binary: 0 if clear protocol, 1 if ambiguous
        """
        # Check if institutional protocol exists and is unambiguous
        has_clear_protocol = self._check_protocol(patient_data)

        return 0.0 if has_clear_protocol else 1.0
```

#### 3.2 Uncertainty-Aware Escalation

**Modify:** `trix/triage.py`

```python
class TriageModule:
    """Uncertainty-aware triage."""

    def __init__(self, threshold: float = 0.7,
                 uncertainty_quantifier: UncertaintyQuantifier = None):
        self.threshold = threshold
        self.uncertainty_quantifier = uncertainty_quantifier or UncertaintyQuantifier()

    def assess_with_uncertainty(self, data: Dict) -> Tuple[TriageResult, UncertaintyProfile]:
        """
        Assess risk WITH uncertainty quantification.

        Higher uncertainty → more conservative escalation
        """
        # Get base risk assessment
        base_result = self.assess(data)

        # Quantify uncertainty
        uncertainty = self.uncertainty_quantifier.quantify(data)

        # Adjust risk level based on uncertainty
        adjusted_level = self._adjust_for_uncertainty(
            base_result.risk_level,
            uncertainty.total
        )

        # Create adjusted result
        adjusted_result = TriageResult(
            risk_level=adjusted_level,
            risk_score=base_result.risk_score,
            features=base_result.features,
            metadata={
                **base_result.metadata,
                'uncertainty_total': uncertainty.total,
                'uncertainty_info': uncertainty.information,
                'uncertainty_diag': uncertainty.diagnostic,
                'uncertainty_policy': uncertainty.policy,
                'uncertainty_adjusted': adjusted_level != base_result.risk_level
            },
            timestamp=base_result.timestamp
        )

        return adjusted_result, uncertainty

    def _adjust_for_uncertainty(self, base_level: RiskLevel,
                                uncertainty: float) -> RiskLevel:
        """
        Conservative escalation under uncertainty.

        Monotonic property: higher uncertainty → never lower urgency
        """
        if uncertainty > 0.7:  # High uncertainty
            # Escalate by 1 level if not already CRITICAL
            if base_level == RiskLevel.MINIMAL:
                return RiskLevel.LOW
            elif base_level == RiskLevel.LOW:
                return RiskLevel.MEDIUM
            elif base_level == RiskLevel.MEDIUM:
                return RiskLevel.HIGH
            elif base_level == RiskLevel.HIGH:
                return RiskLevel.CRITICAL

        return base_level  # No adjustment needed
```

---

### **Phase 4: G1-G5 Clinical Mapping (Weeks 11-12)**

#### 4.1 Five-Group Schema

**Create:** `trix/clinical/g1_g5_schema.py`

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class ClinicalGroup(Enum):
    """Five-group patient classification (manuscript Table 2)."""
    G1_IMMEDIATE_EMERGENCY = 1  # Red flags, unstable vitals
    G2_URGENT_SPECIALIST = 2     # High-risk pattern
    G3_EARLY_FOLLOWUP = 3        # Moderate risk/uncertainty
    G4_ROUTINE_CARE = 4          # Low risk
    G5_REASSURANCE = 5           # Minimal risk

@dataclass
class G1G5Classification:
    """Classification result with clinical group."""
    group: ClinicalGroup
    pathway: str  # "ER_NOW", "NEURO_URGENT", etc.
    time_horizon: str  # "immediate", "<24h", "<7days", etc.
    rationale: str
    safety_net: List[str]  # Return precautions
    escalation_criteria: Optional[str]

class G1G5Classifier:
    """Map from risk/uncertainty to G1-G5 clinical groups."""

    def classify(self,
                risk_level: RiskLevel,
                uncertainty_profile: UncertaintyProfile,
                red_flags: List[RedFlag],
                guideline_recommendation: GuidelineRecommendation
                ) -> G1G5Classification:
        """
        Classify patient into G1-G5 group.

        Decision logic (manuscript Algorithm Box 1):
        1. Red flags → G1
        2. High-risk pattern + manageable uncertainty → G2
        3. Moderate risk or moderate uncertainty → G3
        4. Low risk + low uncertainty → G4
        5. Minimal risk + high confidence → G5
        """
        # Step 1: Check red flags
        if red_flags and any(f.severity >= 8 for f in red_flags):
            return G1G5Classification(
                group=ClinicalGroup.G1_IMMEDIATE_EMERGENCY,
                pathway="ER_NOW",
                time_horizon="immediate",
                rationale=f"Red flags: {', '.join([f.description for f in red_flags])}",
                safety_net=["Call 911 if symptoms worsen"],
                escalation_criteria=None
            )

        # Step 2: High-risk pattern
        if risk_level == RiskLevel.CRITICAL or guideline_recommendation.level == "G1":
            return self._classify_g1(red_flags, guideline_recommendation)

        if risk_level == RiskLevel.HIGH and uncertainty_profile.total < 0.5:
            return self._classify_g2(guideline_recommendation)

        # Step 3: Moderate risk or uncertainty
        if risk_level == RiskLevel.MEDIUM or uncertainty_profile.total >= 0.5:
            return self._classify_g3(uncertainty_profile)

        # Step 4: Low risk
        if risk_level == RiskLevel.LOW:
            return self._classify_g4()

        # Step 5: Minimal risk
        return self._classify_g5()

    def _classify_g1(self, red_flags, guideline_rec) -> G1G5Classification:
        """G1: Immediate emergency."""
        return G1G5Classification(
            group=ClinicalGroup.G1_IMMEDIATE_EMERGENCY,
            pathway="ER_NOW",
            time_horizon="immediate (<1 hour)",
            rationale=guideline_rec.rationale,
            safety_net=[
                "Call 911 immediately",
                "Do not drive",
                "Continuous monitoring required"
            ],
            escalation_criteria=None
        )

    # ... similar methods for G2-G5
```

---

### **Phase 5: Comprehensive Testing (Weeks 13-14)**

#### 5.1 Test Structure

```
tests/
├── test_triage.py              # ✓ Exists
├── test_titrate.py             # NEW
├── test_xai.py                 # NEW
├── test_governance.py          # NEW
├── test_pipeline.py            # NEW
├── test_clinical_guidelines.py # NEW
├── test_uncertainty.py         # NEW
├── test_g1_g5_classification.py # NEW
└── integration/
    ├── test_end_to_end.py      # NEW
    └── test_manuscript_cases.py # NEW (validate manuscript examples)
```

#### 5.2 Example Test

```python
# tests/test_clinical_guidelines.py
import pytest
from trix.clinical.acep_dizziness import ACEPDizzinessGuideline

def test_red_flag_detection_thunderclap_headache():
    """Test: Severe headache triggers red flag."""
    guideline = ACEPDizzinessGuideline()

    patient = {
        'symptoms': {
            'headache_severity': 9,  # Severe (0-10 scale)
            'headache_onset': 'sudden'
        }
    }

    red_flags = guideline.check_red_flags(patient)

    assert "new_severe_headache" in red_flags

def test_acep_guideline_g1_classification():
    """Test: Red flags → G1 (immediate ER)."""
    guideline = ACEPDizzinessGuideline()

    patient = {
        'symptoms': {'focal_weakness': True},
        'vitals': {'blood_pressure': '180/110'}
    }

    recommendation = guideline.evaluate(patient)

    assert recommendation.level == "G1"
    assert recommendation.action == "ER_IMMEDIATE"
    assert recommendation.evidence_grade == "A"

def test_acep_hints_positive_central_pattern():
    """Test: AVS + HINTS+ → G2 (urgent neuro)."""
    guideline = ACEPDizzinessGuideline()

    patient = {
        'timing': {
            'onset': 'sudden',
            'duration_hours': 36
        },
        'examination': {
            'head_impulse_test': 'normal',  # Central sign
            'nystagmus': 'direction_changing',  # Central sign
            'skew_deviation': True  # Central sign
        }
    }

    recommendation = guideline.evaluate(patient)

    assert recommendation.level == "G2"
    assert "NEURO" in recommendation.action
```

---

### **Phase 6: Tutorial Notebooks (Weeks 15-16)**

#### 6.1 Notebook Series

```
notebooks/
├── 00_trix_quickstart.ipynb
├── 01_clinical_guidelines.ipynb    # NEW
├── 02_uncertainty_quantification.ipynb  # NEW
├── 03_g1_g5_classification.ipynb   # NEW
├── 04_xai_explanations.ipynb       # NEW (real SHAP/LIME)
├── 05_end_to_end_evaluation.ipynb  # NEW
└── 06_manuscript_validation.ipynb  # NEW (validate claims)
```

#### 6.2 Notebook 01: Clinical Guidelines

```markdown
# Clinical Guideline Integration in TRI-X

## Overview
This notebook demonstrates how TRI-X integrates evidence-based clinical guidelines:
- ACEP dizziness/vertigo (GRACE-3)
- AHA/ASA stroke guidelines
- AAO-HNS BPPV guidelines

## 1. Load Clinical Guidelines

```python
from trix.clinical import ACEPDizzinessGuideline, AHAStrokeGuideline

acep = ACEPDizzinessGuideline()
aha = AHAStrokeGuideline()

print("Loaded clinical guidelines:")
print(f"  - ACEP: {len(acep.RED_FLAGS)} red flags")
print(f"  - AHA: {len(aha.STROKE_SCALES)} assessment scales")
```

## 2. Red Flag Detection

```python
# Example: Patient with sudden severe headache
patient = {
    'symptoms': {
        'headache_severity': 10,
        'onset': 'sudden',
        'visual_disturbance': True
    },
    'vitals': {
        'blood_pressure': '190/115'
    }
}

red_flags = acep.check_red_flags(patient)
print(f"Detected red flags: {red_flags}")

# Expected: ['new_severe_headache', 'unstable_vital_signs']
```

## 3. Guideline-Based Classification

```python
recommendation = acep.evaluate(patient)

print(f"Clinical Group: {recommendation.level}")  # G1
print(f"Action: {recommendation.action}")         # ER_IMMEDIATE
print(f"Evidence Grade: {recommendation.evidence_grade}")  # A
print(f"Rationale: {recommendation.rationale}")
```

## 4. Validation Against Manuscript

Validate that implementation matches manuscript Table 2...
```

---

## Implementation Priority Matrix

| Task | Impact | Effort | Priority | Weeks |
|------|--------|--------|----------|-------|
| Real XAI (SHAP/LIME) | **CRITICAL** | High | **P0** | 3-4 |
| Clinical Guidelines | **CRITICAL** | High | **P0** | 4 |
| Uncertainty System | High | Medium | **P1** | 2 |
| G1-G5 Mapping | High | Medium | **P1** | 2 |
| TiTrATE Triggers | Medium | Medium | **P2** | 2 |
| Testing Suite | **CRITICAL** | High | **P0** | 2 |
| Tutorial Notebooks | Medium | Medium | **P2** | 2 |

**Total: 15-17 weeks**

---

## Success Metrics (Manuscript-Aligned)

### Technical Metrics
- ✅ XAI Fidelity: >90% (vs. >90% claimed)
- ✅ Test Coverage: >80% (vs. 15% current)
- ✅ Red Flag Detection: 100% sensitivity (safety-critical)
- ✅ G1-G5 Classification: Agreement with guidelines >95%

### Validation Metrics (Match Manuscript Claims)
- ⚠️ Sensitivity: Validate claimed 98.7%
- ⚠️ Specificity: Validate claimed 94.3%
- ⚠️ Explanation Fidelity: Validate claimed 96.2%
- ⚠️ Rule Coverage: Validate claimed 99.1%

---

## Next Steps

### Immediate (This Week)
1. Start Phase 1: Clinical Guidelines
2. Create `trix/clinical/` module structure
3. Implement ACEP red flags

### Short-term (Month 1)
1. Complete clinical guideline modules
2. Replace simulated XAI with real SHAP/LIME
3. Add uncertainty quantification

### Medium-term (Months 2-3)
1. G1-G5 classification system
2. Comprehensive testing
3. Tutorial notebooks

### Publication-Ready (Month 4)
1. Validate all manuscript claims
2. Clinical validation with test cases
3. Ready for journal submission

---

**Status:** Plan Complete, Ready for Implementation
**Last Updated:** January 2026
**Contact:** chatchait66@nu.ac.th
