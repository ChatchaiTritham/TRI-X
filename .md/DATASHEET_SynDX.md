# Datasheet: SynDX (Synthetic Diagnostic Dataset)

## Motivation

### For what purpose was the dataset created?

SynDX (Synthetic Diagnostic Dataset) was created to evaluate the TRI-X framework's performance in emergency triage decision support for dizziness and vertigo presentations. The dataset serves as a controlled, reproducible test environment for validating clinical decision logic, explainable AI methods, and safety-first governance mechanisms without relying on real patient data.

**Primary purposes:**
1. Validate SRGL (Screening-First Risk Governance Logic) gates
2. Test DRAS-5 (Decision-Risk-Action States) state machine
3. Evaluate XAI methods (SHAP, LIME, NMF, Counterfactuals)
4. Assess clinical guideline compliance
5. Demonstrate framework feasibility before real-world validation

### Who created the dataset and on behalf of which entity?

**Created by:** Chatchai Tritham (PhD Candidate)
**Institution:** Department of Computer Science and Information Technology, Faculty of Science, Naresuan University, Thailand
**Supervisor:** Chakkrit Snae Namahoot
**Date:** 2025-2026 (PhD Research)
**Funding:** Naresuan University PhD Research Grant

### Who funded the creation of the dataset?

Naresuan University provided PhD research funding. No external commercial funding was involved.

---

## Composition

### What do the instances that comprise the dataset represent?

Each instance represents a **synthetic patient archetype** for a dizziness/vertigo presentation in an emergency department setting. An archetype is a clinically plausible combination of:
- Patient demographics (age, sex)
- Chief complaint (type of dizziness)
- Symptom characteristics (onset, duration, triggers)
- Associated symptoms (headache, nausea, focal signs)
- Risk factors (hypertension, diabetes, cardiovascular disease)
- Vital signs (blood pressure, heart rate)
- Diagnosis label (ground truth for validation)

### How many instances are there in total?

- **Total archetypes generated:** 8,400
- **Training set:** 5,600 archetypes (used for SHAP model training)
- **Validation set:** 2,800 archetypes
- **Test set:** 500 archetypes (used for performance reporting)

### Does the dataset contain all possible instances or is it a sample?

The dataset is a **stratified sample** of clinically plausible combinations from a parameter space of 126,000 total combinations. The sampling process:

1. **Parameter Space Generation:** 126,000 total combinations of features
2. **Constraint Filtering (TiTrATE):** 48% acceptance rate → 60,000 valid combinations
3. **SHAP-Weighted Sampling:** 8,400 archetypes selected based on clinical importance
4. **Stratification:** Ensures coverage of:
   - All 15 diagnoses (balanced representation)
   - Critical scenarios (15% stroke/TIA)
   - Age groups (young, middle, elderly)
   - Risk profiles (low, moderate, high)
   - Symptom acuity (acute, subacute, chronic)

### What data does each instance consist of?

Each instance contains **42 features** across 6 categories:

#### 1. Demographics (2 features)
- `age`: Integer, 18-90 years, discretized in 5-year bins
- `sex`: Categorical, {Male, Female}

#### 2. Chief Complaint (2 features)
- `symptom_type`: Categorical, {vertigo, dizziness, lightheadedness, imbalance}
- `symptom_severity`: Categorical, {mild, moderate, severe}

#### 3. Temporal Features (3 features)
- `onset`: Categorical, {sudden, acute, gradual, episodic}
- `duration`: Categorical, {seconds, minutes, hours, days, chronic}
- `progression`: Categorical, {improving, stable, worsening}

#### 4. Associated Symptoms (10 features, binary)
- `nystagmus`: {0, 1}
- `headache`: {0, 1}
- `nausea_vomiting`: {0, 1}
- `hearing_loss`: {0, 1}
- `tinnitus`: {0, 1}
- `focal_weakness`: {0, 1}
- `diplopia`: {0, 1}
- `dysarthria`: {0, 1}
- `ataxia`: {0, 1}
- `photophobia`: {0, 1}

#### 5. Risk Factors (10 features, binary)
- `age_over_65`: {0, 1}
- `hypertension`: {0, 1}
- `diabetes`: {0, 1}
- `cardiovascular_disease`: {0, 1}
- `atrial_fibrillation`: {0, 1}
- `previous_stroke_tia`: {0, 1}
- `hyperlipidemia`: {0, 1}
- `smoking`: {0, 1}
- `obesity`: {0, 1}
- `family_history_stroke`: {0, 1}

#### 6. Vital Signs (4 features)
- `bp_systolic`: Integer, 90-200 mmHg
- `bp_diastolic`: Integer, 60-120 mmHg
- `heart_rate`: Integer, 50-120 bpm
- `temperature`: Float, 36.0-38.5°C

#### 7. Ground Truth (1 feature)
- `diagnosis`: Categorical, 15 classes:
  1. BPPV (Benign Paroxysmal Positional Vertigo)
  2. Vestibular Neuritis
  3. Labyrinthitis
  4. Meniere's Disease
  5. Vestibular Migraine
  6. Stroke (Posterior Circulation)
  7. TIA (Transient Ischemic Attack)
  8. Orthostatic Hypotension
  9. Cervical Vertigo
  10. Medication-Induced Dizziness
  11. Anxiety/Panic Disorder
  12. Cardiac Arrhythmia
  13. Anemia
  14. Vestibular Schwannoma
  15. Other/Unspecified

### Is there a label or target associated with each instance?

Yes. Each instance has a **diagnosis label** (1 of 15 categories) assigned during archetype generation based on clinical guideline rules. This label serves as:
- **Ground truth** for validation
- **Supervisory signal** for SHAP model training
- **Reference** for counterfactual explanation evaluation

### Is any information missing from individual instances?

**No missing data by design.** SynDX is a complete synthetic dataset where all features are generated simultaneously. Missing data patterns common in real-world EHR are not present.

**Limitation:** This means the framework is not tested on handling missing data, which is common in clinical practice. Future work should introduce controlled missingness patterns.

### Are relationships between individual instances made explicit?

**No explicit relationships.** Each instance is an independent archetype. However, implicit relationships exist:
- Instances with the same diagnosis share symptom patterns (by design from guidelines)
- Instances from the same age group share demographic risk profiles
- Counterfactual pairs (generated separately) are minimal perturbations of test instances

### Are there recommended data splits?

**Yes, predefined splits:**

| Split | Size | Purpose |
|-------|------|---------|
| Train | 5,600 (66.7%) | SHAP model training, NMF factor discovery |
| Validation | 2,800 (33.3%) | Hyperparameter tuning (not used in current version) |
| Test | 500 (6%) | Performance evaluation (reported in paper) |

**Stratification:** All splits are stratified by:
- Diagnosis (proportional representation)
- Risk tier (R1-R5 distribution maintained)
- Age group (balanced across young/middle/elderly)

### Are there any errors, sources of noise, or redundancies in the dataset?

**Errors:** None by design (synthetic generation).

**Noise:** Minimal. Synthetic data is deterministic from guideline rules. Intentional variability introduced via:
- SHAP-weighted probabilistic sampling (adds diversity)
- Continuous feature discretization (introduces binning uncertainty)

**Redundancies:** Some feature redundancy exists:
- `age` and `age_over_65` (by design for rule checking)
- `hypertension` + `diabetes` + `CVD` often co-occur (realistic comorbidity patterns)

**Trade-off:** Redundancy reflects clinical reality where risk factors cluster.

### Is the dataset self-contained, or does it link to or rely on external resources?

**Self-contained.** The dataset is provided as standalone files:
- `syndx_train.csv` (5,600 rows × 42 columns)
- `syndx_val.csv` (2,800 rows × 42 columns)
- `syndx_test.csv` (500 rows × 42 columns)
- `syndx_metadata.json` (feature descriptions, diagnosis codes)

**External dependencies for interpretation:**
- Clinical guidelines (ACEP, AHA/ASA, AAO-HNS) - cited in documentation
- Feature definitions follow standard medical terminology

### Does the dataset contain data that might be considered confidential?

**No.** The dataset is **100% synthetic** with no real patient data. All instances are algorithmically generated from clinical guideline rules.

**Privacy guarantee:** Differential privacy not required since no real data is involved.

### Does the dataset contain data that, if viewed directly, might be offensive, insulting, threatening, or might otherwise cause anxiety?

**No.** The dataset contains only clinical features (symptoms, vitals, demographics) with no personal identifiers, images, or free text.

---

## Collection Process

### How was the data associated with each instance acquired?

Data was **algorithmically generated**, not collected from patients. Generation process:

#### Phase 1: Clinical Knowledge Extraction
- Clinical guidelines (ACEP, AHA/ASA, AAO-HNS) formalized into computational rules
- TiTrATE constraints defined (10 clinical rules)
- Feature domains specified (age ranges, symptom types, etc.)

#### Phase 2: Parameter Space Enumeration
- Cartesian product of all feature domains → 126,000 combinations
- Constraint filtering → 60,000 valid archetypes (48% acceptance rate)

#### Phase 3: SHAP-Weighted Sampling
- XGBoost classifier trained on valid archetypes
- SHAP values computed for feature importance
- Probabilistic sampling weighted by importance → 8,400 archetypes

#### Phase 4: Stratified Splitting
- 5,600 train, 2,800 validation, 500 test
- Stratification by diagnosis, risk tier, age group

### What mechanisms or procedures were used to collect the data?

**Software tools:**
- Python 3.10
- NumPy 1.24 (array operations)
- Pandas 2.0 (data manipulation)
- XGBoost 2.0 (SHAP importance model)
- SHAP 0.42 (feature importance)
- scikit-learn 1.3 (NMF, sampling)

**Custom modules:**
- `syndx.phase1_knowledge`: Guideline formalization
- `syndx.phase2_synthesis`: Archetype generation
- `syndx.phase3_validation`: Quality checks

**Random seed:** 42 (for reproducibility)

### If the dataset is a sample from a larger set, what was the sampling strategy?

**Two-stage stratified sampling:**

1. **Stage 1: Constraint-Based Filtering**
   - Population: 126,000 total combinations
   - Filter: TiTrATE clinical constraints
   - Result: 60,000 valid archetypes (48%)

2. **Stage 2: SHAP-Weighted Sampling**
   - Population: 60,000 valid archetypes
   - Weights: SHAP feature importance scores
   - Sample size: 8,400 archetypes (14%)
   - Stratification: Diagnosis, risk tier, age group

**Rationale:** SHAP weighting ensures high-importance clinical features are well-represented, improving dataset clinical relevance.

### Who was involved in the data collection process and how were they compensated?

**No human data collection.** Dataset generation was fully automated by the PhD researcher (Chatchai Tritham).

**Expert validation (post-generation):**
- 3 clinical experts (neurologists, ENT specialists)
- Reviewed 20 counterfactual examples for plausibility
- Compensated via academic collaboration (co-authorship)

### Over what timeframe was the data collected?

**Generation period:** November 2025 - January 2026 (3 months)

**Iterative refinement:**
- Version 1.0: Initial 5,000 archetypes (Nov 2025)
- Version 2.0: Expanded to 8,400 with improved constraints (Dec 2025)
- Version 3.0: Final stratified splits (Jan 2026)

### Were any ethical review processes conducted?

**Not required for synthetic data.** Naresuan University IRB determined that synthetic data generation does not constitute human subjects research.

**However:**
- Research protocol reviewed by PhD committee
- Commitment to responsible use (research only, not clinical deployment)
- Ethical disclaimers in all documentation

---

## Preprocessing / Cleaning / Labeling

### Was any preprocessing/cleaning/labeling of the data done?

**Yes, during generation:**

1. **Constraint Validation:** All archetypes checked against 10 TiTrATE rules
   - Invalid combinations rejected
   - Example: "Stroke requires age ≥50 OR vascular risk factors"

2. **Feature Normalization:**
   - Age discretized into 5-year bins
   - Vital signs checked for physiological plausibility
   - Categorical features validated against predefined sets

3. **Diagnosis Assignment:**
   - Labels assigned deterministically based on symptom patterns
   - Guideline-based decision trees used
   - Ambiguous cases flagged (none in final dataset)

4. **Quality Checks:**
   - No duplicate archetypes
   - Balanced diagnosis distribution (χ² test: p > 0.05)
   - Critical scenario coverage (15% stroke/TIA)

### Was the "raw" data saved in addition to the preprocessed/cleaned/labeled data?

**Yes.** Three versions retained:

1. **Raw parameter space:** 126,000 combinations (before constraints)
2. **Valid archetypes:** 60,000 after constraint filtering
3. **Final dataset:** 8,400 after SHAP-weighted sampling

**Storage:** Available in `data/intermediate/` directory (not distributed with main dataset to reduce size)

### Is the software that was used to preprocess/clean/label the data available?

**Yes, fully open-source:**

- **Repository:** https://github.com/ChatchaiTritham/SynDX
- **Key modules:**
  - `syndx/phase1_knowledge/titrate_formalizer.py` - Constraint definitions
  - `syndx/phase2_synthesis/archetype_generator.py` - Generation logic
  - `syndx/phase3_validation/quality_checker.py` - Quality assurance

- **License:** MIT License
- **Documentation:** Complete API documentation in `docs/`

---

## Uses

### Has the dataset been used for any tasks already?

**Yes, in PhD research:**

1. **TRI-X Framework Validation:**
   - SRGL gate evaluation (98% critical detection)
   - DRAS-5 state machine testing (0% safety violations)
   - ORASR routing verification (90.2% pathway match)

2. **XAI Method Evaluation:**
   - SHAP stability analysis (Kendall τ ≈ 0)
   - Counterfactual generation (70% success rate)
   - NMF phenotype discovery (10 factors, 94.8% consistency)

3. **Comparative Analysis:**
   - Benchmarked against MedGAN, Synthea, CTGAN
   - Diagnostic utility gap: 0.7% (vs archetype)

**Publications:** Manuscript in preparation for CS Q2 journal (2026)

### Is there a repository that links to any or all papers or systems that use the dataset?

**Primary repository:** https://github.com/ChatchaiTritham/TRI-X

**Related repositories:**
- https://github.com/ChatchaiTritham/SynDX (dataset generation framework)
- https://github.com/ChatchaiTritham/DRAS-5 (5-state risk machine)
- https://github.com/ChatchaiTritham/ORASR (safety routing)

**Zenodo DOI:** (To be assigned upon publication)

### What (other) tasks could the dataset be used for?

**Potential research applications:**

1. **Clinical Decision Support Development:**
   - Prototyping triage algorithms
   - Testing explainability methods
   - Evaluating safety governance logic

2. **Machine Learning Research:**
   - Benchmarking classifiers (XGBoost, Random Forest, Neural Networks)
   - Testing uncertainty quantification methods
   - Evaluating fairness metrics

3. **Educational Use:**
   - Teaching clinical decision-making logic
   - Demonstrating XAI techniques
   - Training students in medical informatics

4. **Synthetic Data Method Validation:**
   - Comparing archetype-based vs generative (GAN/VAE) approaches
   - Evaluating clinical plausibility metrics

**Out-of-scope uses:**
- ❌ Training clinical deployment models (requires real data)
- ❌ Replacing clinical trials or retrospective studies
- ❌ Generating synthetic patient records for EHR testing (different domain)

### Are there tasks for which the dataset should not be used?

**Prohibited uses:**

1. **Clinical Deployment:** Never use models trained solely on SynDX for real patient care
2. **Regulatory Submission:** Not a substitute for real-world validation required by FDA/EMA
3. **Claims of Clinical Validity:** Performance on SynDX does not imply real-world performance
4. **Privacy Research:** Not suitable for differential privacy or de-identification studies (no real data)
5. **Generalization Beyond Vestibular:** Dataset specific to dizziness/vertigo; do not generalize to other ED complaints

### Any other comments?

**Important limitations:**

1. **Synthetic nature:** Performance on SynDX may not reflect real-world performance
2. **Single domain:** Vestibular disorders only; not representative of general ED triage
3. **No longitudinal data:** Static snapshots; no temporal progression
4. **Idealized data:** No missing values, measurement errors, or data entry mistakes common in real EHR

**Recommended next steps for researchers:**

- Use SynDX for **prototyping and feasibility testing only**
- Follow staged clinical validation pathway (retrospective → prospective → RCT)
- Obtain IRB approval before any patient-related use
- Report SynDX results as "proof-of-concept," not "clinical validation"

---

## Distribution

### Will the dataset be distributed to third parties outside of the entity on behalf of which the dataset was created?

**Yes, publicly available** under open-source license.

**Distribution channels:**
1. **GitHub:** https://github.com/ChatchaiTritham/TRI-X/data/
2. **Zenodo:** (DOI to be assigned upon publication)
3. **Institutional Repository:** Naresuan University Digital Library

**License:** MIT License (permissive, allows commercial and academic use)

### How will the dataset be distributed?

**Formats:**
- CSV files (`syndx_train.csv`, `syndx_val.csv`, `syndx_test.csv`)
- JSON metadata (`syndx_metadata.json`)
- Parquet (optional, for large-scale experiments)

**Download methods:**
- Direct download from GitHub releases
- `git clone` repository
- Zenodo DOI download

**Size:** ~15 MB total (uncompressed CSV)

### When will the dataset be distributed?

**Initial release:** Upon PhD dissertation publication (projected: June 2026)

**Pre-release access:** Available to academic collaborators upon request (email: chatchait66@nu.ac.th)

### Will the dataset be distributed under a copyright or other intellectual property license?

**License:** MIT License

**Key terms:**
- Free to use, modify, distribute
- Commercial and academic use allowed
- Attribution required (cite original work)
- No warranty (use at own risk)

**Copyright holder:** Chatchai Tritham / Naresuan University

### Have any third parties imposed IP-based or other restrictions on the data?

**No.** Dataset is original work by the PhD researcher. No third-party data sources or proprietary tools were used.

### Do any export controls or other regulatory restrictions apply to the dataset?

**No.** Dataset is synthetic medical data with no:
- Real patient information
- Dual-use technology
- Export-controlled algorithms
- Sensitive geopolitical content

**Freely distributable worldwide.**

---

## Maintenance

### Who will be supporting/hosting/maintaining the dataset?

**Primary maintainer:** Chatchai Tritham (chatchait66@nu.ac.th)

**Institutional support:** Department of Computer Science and Information Technology, Naresuan University

**Hosting:**
- GitHub (ChatchaiTritham/TRI-X repository)
- Zenodo (permanent DOI archive)

**Expected maintenance period:** Minimum 5 years (until 2031)

### How can the owner/curator/manager of the dataset be contacted?

**Email:** chatchait66@nu.ac.th

**GitHub Issues:** https://github.com/ChatchaiTritham/TRI-X/issues

**GitHub Discussions:** https://github.com/ChatchaiTritham/TRI-X/discussions

**Institutional address:**
Department of Computer Science and Information Technology
Faculty of Science, Naresuan University
Phitsanulok 65000, Thailand

### Is there an erratum?

**Current version:** 3.0 (January 2026)

**Known issues:** None reported (dataset generated algorithmically)

**Errata will be documented in:** `CHANGELOG.md` in repository

### Will the dataset be updated?

**Planned updates:**

- **Version 4.0 (projected: 2027):** Add longitudinal temporal sequences
- **Version 5.0 (projected: 2028):** Introduce controlled missingness patterns
- **Version 6.0 (future):** Extend to additional ED complaint domains (chest pain, abdominal pain)

**Notification:** Updates announced via:
- GitHub releases
- Zenodo version updates
- Email to registered users (opt-in)

### If the dataset relates to people, are there applicable limits on the retention of the data?

**Not applicable.** Dataset is 100% synthetic with no real patient data.

**However:** Best practice retention policy adopted:
- Data retained for 10 years minimum (until 2036)
- Permanent archival via Zenodo (DOI persistence)
- No deletion planned (supports reproducibility)

### Will older versions of the dataset continue to be supported/hosted/maintained?

**Yes.** All versions archived permanently via:
- GitHub tags/releases (all versions accessible)
- Zenodo (each version has unique DOI)

**Rationale:** Supports reproducibility - researchers can access exact version used in published papers.

### If others want to extend/augment/build on/contribute to the dataset, is there a mechanism for them to do so?

**Yes, contributions welcome:**

**Contribution mechanisms:**
1. **GitHub Pull Requests:** Propose new features, diagnoses, or constraints
2. **GitHub Issues:** Report bugs or suggest improvements
3. **GitHub Discussions:** Discuss new use cases or methodological improvements
4. **Fork repository:** Create custom variants (attribution required)

**Contribution guidelines:** See `CONTRIBUTING.md` in repository

**Review process:** All contributions reviewed by maintainer before merging

---

## References

### Dataset Documentation Standard
Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., & Crawford, K. (2021). Datasheets for datasets. *Communications of the ACM*, 64(12), 86-92.

### Clinical Guidelines Used
- ACEP Clinical Policy: Evaluation and Management of Adults with Acute Dizziness (2017)
- AHA/ASA Guidelines for Prevention of Stroke (2021)
- AAO-HNS Clinical Practice Guideline: Benign Paroxysmal Positional Vertigo (2017)

### Related Publications
*Manuscript in preparation for CS Q2 journal (2026)*

---

**Datasheet Version:** 1.0
**Last Updated:** 2026-01-28
**Author:** Chatchai Tritham
**License:** MIT License

---

**For questions or clarifications about this datasheet, please contact:**
Chatchai Tritham (chatchait66@nu.ac.th)
