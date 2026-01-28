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
- **[API.md](docs/API.md)** - Complete API documentation
- **[GUIDELINES.md](docs/GUIDELINES.md)** - Clinical guidelines reference
- **[XAI_METHODS.md](docs/XAI_METHODS.md)** - Explainability techniques
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contributing guidelines

---

## 🗂️ Repository Structure

```
TRI-X/
├── trix/ # Main package
│ ├── __init__.py
│ ├── triage.py # Triage module
│ ├── titrate.py # TiTrATE engine
│ ├── xai.py # XAI interface
│ ├── governance.py # SRGL implementation
│ ├── pipeline.py # Integrated pipeline
│ └── cli.py # Command-line interface
├── notebooks/ # Jupyter notebooks
│ ├── 01_trix_introduction.ipynb
│ ├── 02_clinical_guidelines.ipynb
│ ├── 03_srgl_gates.ipynb
│ ├── 04_xai_explanations.ipynb
│ └── 05_validation_study.ipynb
├── scripts/ # Utility scripts
│ ├── demo.py
│ ├── generate_figures.py
│ └── run_validation.py
├── tests/ # Unit tests
│ ├── test_triage.py
│ ├── test_titrate.py
│ ├── test_xai.py
│ └── test_pipeline.py
├── data/ # Sample datasets
│ └── validation/
├── docs/ # Documentation
├── outputs/ # Generated outputs
├── setup.py # Package setup
├── requirements.txt # Dependencies
├── CITATION.cff # Citation metadata
├── LICENSE # MIT License
└── README.md # This file
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

## 📧 Contact

### Author

**Chatchai Tritham** (PhD Candidate)

- Email: <chatchait66@nu.ac.th>
- Department of Computer Science and Information Technology
- Faculty of Science, Naresuan University
- Phitsanulok 65000, Thailand

### Supervisor

Chakkrit Snae Namahoot

- Email: <chakkrits@nu.ac.th>
- Department of Computer Science and Information Technology
- Faculty of Science, Naresuan University
- Phitsanulok 65000, Thailand

### For Questions or Collaborations

- GitHub Issues: <https://github.com/ChatchaiTritham/TRI-X/issues>
- GitHub Discussions: <https://github.com/ChatchaiTritham/TRI-X/discussions>
- Email: <chatchait66@nu.ac.th>

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
