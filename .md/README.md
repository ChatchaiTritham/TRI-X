# TRI-X: Triage-TiTrATE-XAI Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status: Research](https://img.shields.io/badge/status-research-orange.svg)]()
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.XXXXXX-blue)](https://doi.org/10.5281/zenodo.XXXXXX)

**TRI-X** integrates three components: **Triage** (clinical guidelines), **TiTrATE** (time-triggered actions), and **XAI** (explainability) to create a transparent, auditable emergency triage system based on Screening-First Risk Governance Logic (SRGL).

Part of the integrated emergency triage trilogy: **TRI-X** | [DRAS-5](https://github.com/ChatchaiTritham/DRAS-5) | [ORASR](https://github.com/ChatchaiTritham/ORASR)

---

## 🎯 Overview

### What is TRI-X?

TRI-X is a novel framework that combines:
- **Triage**: Evidence-based clinical guidelines (ACEP, AHA/ASA, AAO-HNS).
- **TiTrATE**: Targeted Integration of Triage Rules and Algorithmic Triage Evaluation.
- **XAI**: Explainable interpretability using SHAP, LIME, and rule-based explanations.

### Screening-First Risk Governance Logic (SRGL)

TRI-X uses **SRGL**, a transparent, rule-based approach where:
1. Clinical guidelines are prioritized over machine learning predictions.
2. Risk gates enforce safety constraints.
3. Explanations are generated for every decision.
4. Human oversight is maintained at all times.

---

## 🚀 Quick Start

Get running in 5 minutes:

```bash
# Clone and setup
git clone https://github.com/ChatchaiTritham/TRI-X.git && cd TRI-X
python -m venv venv && source venv/bin/activate # Windows: venv\Scripts\activate
pip install -r requirements.txt && pip install -e .

# Run demo
python scripts/demo.py

# Or launch Jupyter notebook
jupyter lab notebooks/01_trix_introduction.ipynb
```

📖 **See [QUICKSTART.md](QUICKSTART.md) for detailed step-by-step guide**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ TRI-X Framework Architecture │
├─────────────────────────────────────────────────────────────┤
│ │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────┐ │
│ │ Triage │ → │ TiTrATE │ → │ XAI │ │
│ │ Guidelines │ │ Framework │ │ Layer │ │
│ └──────────────┘ └──────────────┘ └──────────┘ │
│ ↓ ↓ ↓ │
│ Clinical Rules Diagnostic Logic Explanations │
│ (ACEP, AHA) (Red flags, (SHAP, LIME, │
│ Risk factors) Rules) │
│ │
│ ┌──────────────────────────────────────────────────────┐ │
│ │ SRGL (Screening-First Risk Governance Logic) │ │
│ │ • Gate G1: Critical red flags │ │
│ │ • Gate G2: Risk factor assessment │ │
│ │ • Gate G3: Uncertainty quantification │ │
│ └──────────────────────────────────────────────────────┘ │
│ ↓ │
│ Risk Tier (R1-R5) + Explanation │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Features

### 1. Clinical Guideline Integration
- ACEP Dizziness/Vertigo Guidelines
- AHA/ASA Stroke Guidelines
- AAO-HNS BPPV Guidelines
- Red flag detection system

### 2. TiTrATE Diagnostic Framework
- Symptom pattern matching
- Risk factor scoring
- Temporal analysis (onset, duration, progression)
- Comorbidity assessment

### 3. XAI Explainability Layer
- **SHAP values**: Feature importance for each decision
- **LIME**: Local interpretable model explanations
- **NMF (Non-negative Matrix Factorization)**: Pattern discovery and clinical phenotype identification
- **Rule extraction**: Human-readable decision rules
- **Counterfactual explanations**: "What if" scenarios

### 4. SRGL Risk Gates
- **Gate G1**: Critical red flags (stroke signs, etc.)
- **Gate G2**: Risk factors (age, CVD, diabetes)
- **Gate G3**: Uncertainty quantification
- **Merging strategy**: Conservative (max risk) or balanced

---

## 📊 Performance Metrics

Evaluated on 500 synthetic test cases (SynDX dataset):

| Metric | Value | Target |
| ------ | ----- | ------ |
| Critical Alert Detection | 98.0% | ≥ 95% |
| Safety Boundary Violations | 0.0% | 0% |
| TiTrATE Compliance | 98.0% | ≥ 95% |
| ESI Triage Agreement | 93.4% | ≥ 90% |
| Red Flag Detection (No Miss) | 100% | 100% |
| Explanation Consistency | 98.4% | ≥ 95% |
| Care Pathway Match | 90.2% | ≥ 85% |

**Note:** Performance validated on synthetic data (SynDX). Clinical validation required before deployment.

---

## 🎯 Usage

### Python API

```python
from trix import TRIXFramework
from trix.explainability import SHAPExplainer

# Initialize framework
trix = TRIXFramework(
 guidelines=['ACEP', 'AHA', 'AAO'],
 srgl_mode='conservative'
)

# Patient case
patient = {
 'age': 68,
 'sex': 'M',
 'chief_complaint': 'acute_vertigo',
 'onset': 'sudden',
 'red_flags': ['new_focal_weakness'],
 'risk_factors': ['hypertension', 'diabetes'],
 'vital_signs': {
 'bp_systolic': 168,
 'heart_rate': 92
 }
}

# Get triage decision
decision = trix.evaluate(patient)
print(f"Risk Tier: {decision.risk_tier}") # R2 (High Risk)
print(f"Urgency: {decision.urgency}") # Emergency
print(f"Confidence: {decision.confidence:.3f}")

# Get explanation
explainer = SHAPExplainer(trix)
explanation = explainer.explain(patient)

print("\n=== EXPLANATION ===")
print(f"Top risk factors:")
for feature, importance in explanation.top_features(n=5):
 print(f" • {feature}: {importance:.3f}")
```

**Output:**
```
Risk Tier: R2 (High Risk - Emergency)
Urgency: Emergency
Confidence: 0.947

=== EXPLANATION ===
Top risk factors:
 • new_focal_weakness: 0.842
 • age > 65: 0.234
 • hypertension: 0.156
 • diabetes: 0.098
 • sudden_onset: 0.087
```

---

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[MODEL_CARD.md](MODEL_CARD.md)** - Model documentation and ethical considerations
- **[DATASHEET_SynDX.md](DATASHEET_SynDX.md)** - Dataset documentation (SynDX)
- **[API.md](docs/API.md)** - Complete API documentation
- **[GUIDELINES.md](docs/GUIDELINES.md)** - Clinical guidelines reference
- **[XAI_METHODS.md](docs/XAI_METHODS.md)** - Explainability techniques
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contributing guidelines

---

## 🗂️ Repository Structure

```
TRI-X/
├── trix/                          # Main package
│   ├── __init__.py
│   ├── triage.py                  # Triage module
│   ├── titrate.py                 # TiTrATE engine
│   ├── xai.py                     # XAI interface
│   ├── governance.py              # SRGL implementation
│   ├── pipeline.py                # Integrated pipeline
│   └── cli.py                     # Command-line interface
├── examples/                      # Visualization examples
│   ├── trix_visualizations.py     # Main figures (7 figures)
│   ├── framework_diagrams.py      # Framework diagrams (3 figures)
│   └── __init__.py
├── notebooks/                     # Jupyter notebooks
│   ├── 01_trix_introduction.ipynb
│   ├── 02_clinical_guidelines.ipynb
│   ├── 03_srgl_gates.ipynb
│   ├── 04_xai_explanations.ipynb
│   └── 05_validation_study.ipynb
├── scripts/                       # Utility scripts
│   ├── demo.py
│   ├── generate_figures.py
│   └── run_validation.py
├── tests/                         # Unit tests
│   ├── test_triage.py
│   ├── test_titrate.py
│   ├── test_xai.py
│   └── test_pipeline.py
├── data/                          # Sample datasets
│   └── validation/
├── docs/                          # Documentation
│   ├── API.md
│   ├── GUIDELINES.md
│   └── XAI_METHODS.md
├── outputs/                       # Generated outputs
│   ├── figures/                   # Publication-ready figures (PNG + PDF)
│   └── validation/                # Validation results
├── MODEL_CARD.md                  # Model card (ethics, performance, limitations)
├── DATASHEET_SynDX.md             # Dataset documentation (SynDX)
├── QUICKSTART.md                  # Quick start guide
├── CONTRIBUTING.md                # Contributing guidelines
├── setup.py                       # Package setup
├── requirements.txt               # Dependencies
├── CITATION.cff                   # Citation metadata
├── LICENSE                        # MIT License
└── README.md                      # This file
```

---

## ⚠️ Safety & Limitations

### 🚨 NOT FOR CLINICAL USE

This is **research software only**:
- ❌ Not FDA-cleared or CE-marked
- ❌ Not validated on real patient data
- ❌ Requires IRB approval for studies
- ✅ Always maintain human oversight

### Limitations

1. **Rule-based scope**: Limited to guideline-covered scenarios
2. **Single domain**: Dizziness/vertigo only (not general ED triage)
3. **Synthetic validation**: Validated on synthetic cases, not real EHR
4. **Explanation quality**: XAI methods approximate, not ground truth

### ⚖️ Fairness & Bias

**Bias Assessment:**

TRI-X has been evaluated for potential biases across demographic groups:

**Age Bias:**
- **Finding:** Elderly patients (>65) may be systematically over-triaged due to age-based risk factors
- **Mitigation:** SHAP explanations make age contribution transparent, allowing clinicians to assess appropriateness
- **Monitoring:** Performance tracked separately for age subgroups (young <50, middle 50-65, elderly >65)
- **Results:** Sensitivity maintained across age groups: 97.3% (young), 98.7% (middle), 98.1% (elderly)

**Sex/Gender Bias:**
- **Finding:** Some diagnoses have sex-specific prevalence (e.g., vestibular migraine more common in females)
- **Mitigation:** Prevalence reflects clinical epidemiology from guidelines, not social bias
- **Monitoring:** Performance tracked by sex: Male 94.2%, Female 93.8% (no significant difference, p=0.72)

**Socioeconomic & Racial Bias:**
- **Limitation:** SynDX does not include socioeconomic status, race, or ethnicity features
- **Impact:** Framework not tested for disparities related to social determinants of health
- **Future Work:** Real-world validation must assess fairness across diverse patient populations

**Fairness Metrics (SynDX Validation):**
- Demographic Parity: χ² test for risk tier distribution by age/sex (p > 0.05, no significant bias)
- Equalized Odds: Sensitivity and specificity within 5% across all subgroups
- Calibration: Predicted risk aligned with observed risk tier across subgroups

**Commitment:**
- All model decisions are explainable (XAI layer)
- Bias monitoring built into ORASR audit trail
- Regular fairness audits recommended for any deployment

### 🛣️ Clinical Validation Roadmap

**IMPORTANT:** TRI-X is currently validated only on synthetic data. Before any clinical deployment, the following **staged validation pathway** is MANDATORY:

#### Stage 1: Retrospective Validation (12-18 months)

**Objective:** Validate on historical patient data

- Collect de-identified ED patient records (IRB approval required)
- Minimum 1,000 dizziness/vertigo cases from ≥2 hospitals
- Compare TRI-X decisions to actual clinical outcomes (30-day adverse events)
- **Success Criteria:**
  - Sensitivity ≥95% for critical diagnoses (stroke, TIA)
  - Zero missed strokes (NPV 100%)
  - False positive rate <10%

#### Stage 2: Prospective Observational Study (18-24 months)

**Objective:** Test in real-time clinical workflow (shadow mode)

- Deploy TRI-X in shadow mode (no impact on actual care)
- Clinicians see TRI-X recommendations but make independent decisions
- Compare TRI-X vs clinician decisions and patient outcomes
- Minimum 2,000 patients, ≥50 clinicians, ≥5 hospitals
- **Success Criteria:**
  - Agreement with expert clinicians ≥90%
  - Clinician acceptance score ≥4/5
  - Explanation utility rated ≥3.5/5

#### Stage 3: Randomized Controlled Trial (24-36 months)

**Objective:** Demonstrate non-inferior or superior patient outcomes

- Cluster-randomized trial: TRI-X-assisted triage vs standard triage
- Primary endpoint: 30-day adverse event rate
- Secondary endpoints: Time to diagnosis, resource utilization, ED length of stay
- Minimum 5,000 patients across ≥10 sites
- **Success Criteria:**
  - Non-inferiority for patient safety (adverse events)
  - Superiority for efficiency (time to diagnosis, resource use)

#### Stage 4: Regulatory Approval (12-24 months)

**Objective:** Obtain regulatory clearance for clinical use

- **USA:** FDA 510(k) clearance or De Novo pathway (Software as Medical Device)
- **Europe:** CE marking (Medical Device Regulation)
- **Other jurisdictions:** Country-specific approval
- Post-market surveillance plan required
- **Success Criteria:**
  - Regulatory approval obtained
  - Post-market monitoring activated

#### Stage 5: Implementation & Continuous Monitoring (Ongoing)

**Objective:** Safe deployment and continuous quality improvement

- Real-world deployment in partner hospitals
- Continuous performance monitoring (monthly reports)
- Fairness audits every 6 months
- Model retraining and updates (annual)
- Adverse event reporting system
- **Success Criteria:**
  - Sustained performance (annual review)
  - No safety signals detected
  - User satisfaction maintained

**Total Timeline:** 5-9 years from current prototype to full clinical deployment

**Current Status:** Stage 0 (Proof-of-Concept with Synthetic Data)

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 📖 Citation

```bibtex
@software{trix2026,
 author = {Tritham, Chatchai},
 title = {TRI-X: Triage-TiTrATE-XAI Framework for Explainable Emergency Triage},
 year = {2026},
 publisher = {GitHub},
 url = {https://github.com/ChatchaiTritham/TRI-X},
 note = {Screening-First Risk Governance Logic (SRGL). PhD Research.}
}
```

### Related Publications

*Manuscript in preparation for CS Q2 journal*

---

## 🔗 Related Projects

Part of the **Emergency Triage Decision Support** trilogy:

1. **TRI-X** (this repo) - Triage-TiTrATE-XAI Framework
2. [**DRAS-5**](https://github.com/ChatchaiTritham/DRAS-5) - 5-State Risk Machine
3. [**ORASR**](https://github.com/ChatchaiTritham/ORASR) - Operational Reasoning-Action Safety Routing

---

## 🎓 Academic Context

**Institution**: Naresuan University, Thailand
**Department**: Computer Science and Information Technology
**Degree**: PhD in Computer Science
**Research Area**: Clinical Decision Support, Explainable AI, Healthcare Informatics

---

**Built with transparency. Every decision explainable. Every rule auditable.** 🔍

---

*Last Updated: 2026-01-09 | Version: 1.0.0 | Status: Research*
