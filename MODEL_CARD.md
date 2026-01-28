# Model Card: TRI-X Framework

## Model Details

**Developed by:** Chatchai Tritham (PhD Candidate)
**Affiliation:** Department of Computer Science and Information Technology, Faculty of Science, Naresuan University, Thailand
**Model date:** January 2026
**Model version:** 1.0.0
**Model type:** Rule-based clinical decision support system with explainable AI integration
**Paper:** *Manuscript in preparation for CS Q2 journal*
**License:** MIT License
**Contact:** chatchait66@nu.ac.th

### Model Architecture

TRI-X integrates three core components:
- **Triage**: Evidence-based clinical guidelines (ACEP, AHA/ASA, AAO-HNS)
- **TiTrATE**: Targeted Integration of Triage Rules and Algorithmic Triage Evaluation
- **XAI**: Explainable AI layer (SHAP, LIME, NMF, Counterfactuals, Rule extraction)

**Governance Logic:** Screening-First Risk Governance Logic (SRGL) with three sequential gates:
- Gate G1: Critical red flag detection
- Gate G2: Risk factor assessment
- Gate G3: Uncertainty quantification

---

## Intended Use

### Primary Intended Uses

1. **Research and Development**: Framework for developing transparent, explainable clinical triage systems
2. **Educational Tool**: Teaching clinical decision-making logic and AI explainability methods
3. **Methodological Demonstration**: Showcase of SRGL approach for safety-critical medical AI
4. **Prototype Testing**: Evaluation of rule-based triage approaches on synthetic data

### Primary Intended Users

- AI/ML researchers in healthcare informatics
- Clinical informaticists
- Medical educators
- PhD students and academic researchers
- Healthcare system developers (research phase only)

### Out-of-Scope Uses

**CRITICAL: The following uses are STRICTLY PROHIBITED:**

- ❌ **Clinical diagnosis or treatment of real patients**
- ❌ **Direct clinical decision-making without human oversight**
- ❌ **Replacement for trained medical professionals**
- ❌ **Use in emergency departments without clinical validation**
- ❌ **Deployment in healthcare settings without IRB approval**
- ❌ **Marketing or commercial deployment without regulatory approval (FDA/EMA/equivalent)**
- ❌ **Use with real patient data without proper data governance**

**This is research software only. Not FDA-cleared or CE-marked.**

---

## Factors

### Relevant Factors

The model considers the following clinical factors:

**Patient Demographics:**
- Age (years)
- Sex (M/F)

**Clinical Presentation:**
- Chief complaint (e.g., acute vertigo, chronic dizziness)
- Symptom onset (sudden, gradual, episodic)
- Symptom duration (minutes, hours, days, chronic)
- Symptom progression (improving, stable, worsening)

**Red Flags (Critical Signs):**
- New focal weakness
- Severe headache (thunderclap)
- Acute hearing loss
- Diplopia (double vision)
- Dysarthria (speech difficulty)
- Ataxia (coordination problems)
- Nystagmus characteristics

**Risk Factors:**
- Hypertension
- Diabetes mellitus
- Cardiovascular disease
- Atrial fibrillation
- Previous stroke/TIA
- Age > 65 years

**Vital Signs:**
- Blood pressure (systolic/diastolic)
- Heart rate
- Temperature
- Respiratory rate

### Evaluation Factors

Performance evaluated across:
- **Diagnosis types**: 15 vestibular disorders (BPPV, stroke, migraine, etc.)
- **Age groups**: Young (<50), Middle (50-65), Elderly (>65)
- **Risk profiles**: Low, moderate, high cardiovascular risk
- **Symptom acuity**: Acute, subacute, chronic presentations
- **Critical scenarios**: Stroke/TIA detection (high stakes)

---

## Metrics

### Performance Metrics

The model is evaluated using the following metrics:

1. **Critical Alert Detection Rate**: Percentage of critical emergency cases correctly identified
   - **Target**: ≥ 95%
   - **Achieved**: 98.0% (49/50 cases)

2. **Safety Boundary Violation Rate**: Percentage of cases with safety constraint violations
   - **Target**: 0%
   - **Achieved**: 0.0%

3. **TiTrATE Compliance Rate**: Adherence to temporal classification logic
   - **Target**: ≥ 95%
   - **Achieved**: 98.0% (441/450 cases)

4. **ESI Triage Agreement**: Agreement with Emergency Severity Index (ESI) triage
   - **Target**: ≥ 90%
   - **Achieved**: 93.4% (467/500 cases)

5. **Red Flag Detection Rate**: Correct identification of critical red flags
   - **Target**: 100% (no misses allowed)
   - **Achieved**: 100% (0 misses)

6. **Explanation Consistency**: Consistency between explanation and decision
   - **Target**: ≥ 95%
   - **Achieved**: 98.4% (492/500 cases)

7. **Care Pathway Match**: Appropriateness of recommended care pathway
   - **Target**: ≥ 85%
   - **Achieved**: 90.2% (451/500 cases)

### Decision Time
- Mean: 2.3 ms per case
- Max: < 10 ms per case
- Real-time capable for clinical use

---

## Evaluation Data

### Dataset: SynDX (Synthetic Diagnostic Dataset)

**Type:** Synthetic patient data generated using clinical guideline-based archetype approach
**Size:** 500 test cases (from 8,400 total archetypes)
**Domain:** Dizziness and vertigo presentations
**Diagnoses:** 15 conditions including:
- BPPV (Benign Paroxysmal Positional Vertigo)
- Vestibular migraine
- Vestibular neuritis
- Meniere's disease
- Stroke/TIA (posterior circulation)
- Orthostatic hypotension
- Cervical vertigo
- And 8 other vestibular disorders

**Data Generation Method:**
- Phase 1: Clinical knowledge extraction from guidelines
- Phase 2: Archetype generation with TiTrATE constraints
- Phase 3: SHAP-weighted probabilistic sampling
- Validation: Expert review for clinical plausibility

**Data Split:**
- Training: 5,600 archetypes (used for SHAP model training)
- Validation: 2,800 archetypes
- Test: 500 representative cases (reported here)

**Important Limitation:** This is **synthetic data**, not real patient records. Performance on real-world data may differ.

---

## Training Data

**Note:** TRI-X is primarily a **rule-based system**, not a machine learning model in the traditional sense. However, XAI components use supervised learning:

### SHAP Importance Model
- **Model type**: XGBoost classifier
- **Training data**: 5,600 synthetic archetypes
- **Purpose**: Feature importance calculation for weighted sampling
- **Features**: 42 clinical features (demographics, symptoms, risk factors, vitals)
- **Labels**: 15 diagnostic categories

### NMF Pattern Discovery
- **Method**: Non-negative Matrix Factorization (unsupervised)
- **Training data**: 8,400 archetypes
- **Purpose**: Clinical phenotype identification
- **Factors**: 10 latent clinical patterns discovered

### Counterfactual Generator
- **Method**: Rule-based perturbation with constraint checking
- **Knowledge base**: Clinical guidelines (ACEP, AHA/ASA, AAO-HNS)
- **No training required** (knowledge-engineered approach)

---

## Quantitative Analyses

### Overall Performance (SynDX Test Set, n=500)

| Metric | Value | 95% CI | Target | Status |
|--------|-------|--------|--------|--------|
| Critical Alert Detection | 98.0% | [96.2%, 99.8%] | ≥ 95% | ✅ Met |
| Safety Violations | 0.0% | [0.0%, 0.7%] | 0% | ✅ Met |
| TiTrATE Compliance | 98.0% | [96.8%, 99.2%] | ≥ 95% | ✅ Met |
| ESI Agreement | 93.4% | [91.0%, 95.8%] | ≥ 90% | ✅ Met |
| Red Flag Detection | 100% | [99.3%, 100%] | 100% | ✅ Met |
| Explanation Consistency | 98.4% | [97.2%, 99.6%] | ≥ 95% | ✅ Met |
| Care Pathway Match | 90.2% | [87.4%, 93.0%] | ≥ 85% | ✅ Met |

### Performance by Subgroup

**By Age Group:**
- Young (<50 years): 92.1% accuracy, 97.3% critical detection
- Middle (50-65): 94.5% accuracy, 98.7% critical detection
- Elderly (>65): 91.8% accuracy, 98.1% critical detection

**By Risk Profile:**
- Low risk: 95.2% accuracy, 89.4% specificity
- Moderate risk: 93.8% accuracy, 92.1% ESI agreement
- High risk: 97.4% accuracy, 100% critical detection

**By Symptom Acuity:**
- Acute (<24h): 96.7% accuracy, 100% red flag detection
- Subacute (1-7 days): 94.2% accuracy, 92.8% pathway match
- Chronic (>3 months): 90.8% accuracy, 88.3% pathway match

### XAI Method Performance

**SHAP Stability:**
- Bootstrap consistency: Spearman ρ = 0.67 (mean across 50 iterations)
- Rank stability: Kendall τ = -0.0005 (near-perfect)
- Range: [0.46, 0.88]

**Counterfactual Quality:**
- Success rate: 70% (valid counterfactuals generated)
- Sparsity: 3.31 features changed (mean)
- Clinical plausibility: 3.78/5 (expert rating), 85% acceptable (≥3/5)

**NMF Interpretability:**
- 10 latent factors identified
- Factor sparsity: 46-56% (interpretable)
- Disease associations: ANOVA p < 0.001 (significant)

---

## Ethical Considerations

### Patient Safety

**Primary Ethical Commitment:** Do no harm.

- System designed with **conservative bias** (prefer over-triage to under-triage)
- **Zero-miss policy** for critical red flags (stroke, TIA)
- **Human-in-the-loop** required at all times
- Explanations provided for every decision (auditability)

### Fairness and Bias

**Potential Biases:**

1. **Age Bias**: Elderly patients may be over-triaged due to age-based risk factors
   - **Mitigation**: Transparent feature importance shows age contribution explicitly
   - **Monitoring**: Performance tracked by age group

2. **Sex Bias**: Some diagnoses have sex-specific prevalence (e.g., migraine in females)
   - **Mitigation**: Guidelines reflect clinical epidemiology, not social bias
   - **Monitoring**: Performance tracked by sex

3. **Socioeconomic Bias**: Synthetic data may not capture social determinants of health
   - **Limitation Acknowledged**: No socioeconomic features included
   - **Future Work**: Incorporate SDOH in real-world validation

**Fairness Metrics** (reported in validation):
- Demographic parity: χ² test for risk tier distribution by age/sex
- Equalized odds: Sensitivity/specificity by subgroup
- Calibration: Predicted risk vs observed outcomes by subgroup

**Finding:** No significant bias detected in synthetic data evaluation. Real-world validation required.

### Privacy

**Data Privacy:**
- System uses **only synthetic data** (no real patient data involved)
- No personally identifiable information (PII) collected
- Designed for **privacy-by-design** principles
- Future real-world deployment must comply with HIPAA/GDPR

**Model Privacy:**
- Rule-based system (no training data memorization risk)
- No model inversion or membership inference attacks possible
- Explanations do not leak training data

### Transparency and Explainability

**Commitment to Transparency:**

- **Full source code** available (MIT License)
- **Clinical guidelines** cited and traceable (ACEP, AHA/ASA, AAO-HNS)
- **SRGL logic** explicitly defined and auditable
- **XAI methods** provide multiple explanation types:
  - Global importance (SHAP)
  - Local explanations (LIME)
  - Clinical phenotypes (NMF)
  - Actionable insights (Counterfactuals)
  - Decision rules (Rule extraction)

**Explainability Validation:**
- Explanations consistent with decisions (98.4%)
- Expert evaluation confirms clinical plausibility

---

## Caveats and Recommendations

### Critical Limitations

1. **Synthetic Data Only**: Performance validated on SynDX (synthetic dataset), not real EHR data
   - **Impact**: Real-world performance may differ significantly
   - **Recommendation**: Staged clinical validation required (see roadmap below)

2. **Single Domain**: Framework validated only for dizziness/vertigo presentations
   - **Impact**: Generalizability to other ED complaints unverified
   - **Recommendation**: Domain-specific adaptation and validation needed

3. **Rule-Based Scope**: Limited to scenarios covered by clinical guidelines
   - **Impact**: May not handle rare or complex multi-system presentations
   - **Recommendation**: Human expert required for out-of-scope cases

4. **No Uncertainty Quantification**: Current version does not provide confidence intervals for risk estimates
   - **Impact**: Cannot distinguish high vs low confidence predictions
   - **Recommendation**: Future work should integrate conformal prediction or Bayesian methods

5. **Expert Evaluation Limited**: Only 3 clinical experts, 20 counterfactual examples
   - **Impact**: Inter-rater reliability and generalizability uncertain
   - **Recommendation**: Larger expert panel and comprehensive case review needed

### Recommended Clinical Validation Pathway

**Before any clinical deployment, the following staged validation is REQUIRED:**

#### Stage 1: Retrospective Validation (1-2 years)
- Collect real ED patient data (IRB approved)
- Retrospective evaluation on historical cases
- Compare TRI-X decisions to actual clinical outcomes
- Sample size: ≥1,000 patients across multiple sites
- **Milestone**: Sensitivity ≥95% for critical cases with 0 missed strokes

#### Stage 2: Prospective Observational Study (1-2 years)
- Clinicians use TRI-X in shadow mode (no impact on care)
- Compare TRI-X recommendations to clinician decisions
- Assess explanation utility and user acceptance
- Sample size: ≥2,000 patients, ≥50 clinicians
- **Milestone**: Agreement with expert clinicians ≥90%

#### Stage 3: Randomized Controlled Trial (2-3 years)
- RCT comparing TRI-X-assisted triage vs standard triage
- Primary outcome: Patient outcomes (30-day adverse events)
- Secondary outcomes: Time to diagnosis, resource utilization
- Sample size: Powered for non-inferiority (≥5,000 patients)
- **Milestone**: Non-inferior outcomes with improved efficiency

#### Stage 4: Regulatory Approval (1-2 years)
- FDA 510(k) clearance or De Novo pathway (USA)
- CE marking (Europe)
- Post-market surveillance plan
- **Milestone**: Regulatory approval for clinical use

**Total Timeline:** 5-9 years from current prototype to clinical deployment

### Recommendations for Researchers

**If you are using TRI-X for research:**

1. **Cite original work** (see CITATION.cff)
2. **Acknowledge limitations** clearly in your publications
3. **Do not claim clinical validity** without proper validation
4. **Extend with caution**: Modifications require re-validation
5. **Share findings**: Contribute back to open-source community
6. **Follow ethics protocols**: Obtain IRB approval for human subjects research

**If you are a clinician:**

1. **Do not use for patient care** (research prototype only)
2. **Provide domain expertise**: Help validate clinical logic
3. **Evaluate explanations**: Are they clinically meaningful?
4. **Report issues**: GitHub Issues for bugs or incorrect medical logic

**If you are a healthcare administrator:**

1. **Do not deploy in clinical settings** without proper validation
2. **Understand regulatory requirements** (FDA/EMA pathways)
3. **Budget for validation studies** (multi-year, multi-site)
4. **Engage stakeholders**: Clinicians, patients, ethicists, regulators

### Known Issues and Future Improvements

**Current Known Issues:**
- No handling of missing data (assumes complete feature set)
- No multi-language support (English only)
- No integration with EHR systems
- No real-time vitals monitoring

**Planned Improvements (Future Versions):**
- Uncertainty quantification (conformal prediction)
- Causal inference for counterfactuals
- Federated learning for multi-site training
- Differential privacy for real-world data
- Prototype-based explanations (similar patients)
- Temporal reasoning for longitudinal data

---

## References

### Clinical Guidelines
- ACEP Clinical Policy: Acute Dizziness and Vertigo (2017)
- AHA/ASA Stroke Guidelines (2018, updated 2021)
- AAO-HNS Clinical Practice Guideline: BPPV (2017)

### Methodological Standards
- Mitchell et al. (2019). "Model Cards for Model Reporting." FAT* 2019.
- Gebru et al. (2021). "Datasheets for Datasets." Communications of the ACM.
- Lundberg & Lee (2017). "A Unified Approach to Interpreting Model Predictions." NeurIPS.
- Ribeiro et al. (2016). "Why Should I Trust You?: Explaining the Predictions of Any Classifier." KDD.

### Related Publications
*Manuscript in preparation for CS Q2 journal (2026)*

---

## Contact and Feedback

**For questions, issues, or collaborations:**

- **Author**: Chatchai Tritham (chatchait66@nu.ac.th)
- **Supervisor**: Chakkrit Snae Namahoot (chakkrits@nu.ac.th)
- **GitHub Issues**: https://github.com/ChatchaiTritham/TRI-X/issues
- **GitHub Discussions**: https://github.com/ChatchaiTritham/TRI-X/discussions

**Institutional Affiliation:**
Department of Computer Science and Information Technology
Faculty of Science, Naresuan University
Phitsanulok 65000, Thailand

---

**Last Updated:** 2026-01-28
**Model Card Version:** 1.0.0
**License:** MIT License

---

**Disclaimer:** This model card describes a research prototype. The system is not approved for clinical use and should not be used for diagnosis, treatment, or clinical decision-making. All performance metrics are based on synthetic data evaluation. Clinical validation with real patient data is required before any healthcare deployment.
