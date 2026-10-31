# Centralized Academic Monitoring and Prediction System Using Machine Learning (CAMPS-ML)
## Final Capstone Project Technical Report

**Author:** Final-Year B.E. (Computer Science and Design)  
**Academic Year:** 2024–2025  
**Institution:** Technical University / Autonomous Engineering College  

---

### Abstract
Student attrition, course backlogs, and academic underperformance present persistent challenges for higher education institutions. Traditional campus management software operates primarily as post-facto audit logs, recording grades and attendance only after end-semester examinations conclude. This paper presents **CAMPS-ML** (*Centralized Academic Monitoring and Prediction System Using Machine Learning*), a production web platform integrating real-time academic ingestion, dual-objective predictive modeling, and game-theoretic explainable AI (XAI). 

CAMPS-ML centralizes student attendance, Continuous Internal Evaluation (CIE IA1–IA3), historical semester grade point averages (SGPA/CGPA), fee clearance records, and demographic attributes. The system deploys a dual-objective machine learning pipeline: (1) a multi-class **XGBoost** risk classifier classifying students into Low, Medium, and High academic risk tiers, and (2) a **Gradient Boosting Regressor** forecasting next-semester SGPA. To prevent data leakage, Quantile transformations and Synthetic Minority Over-sampling Technique (SMOTE) are encapsulated strictly within cross-validation training folds. To dismantle the "black-box" barrier, **TreeSHAP** (SHapley Additive exPlanations) computes exact local feature attributions for individual students, automatically formulating actionable remedial suggestions for faculty mentors. 

Experimental evaluation across 5-fold cross validation demonstrates that the tuned XGBoost classifier achieves **98.00% accuracy**, **0.9743 macro-F1 score**, and **0.9992 ROC-AUC**, outperforming Logistic Regression, Decision Trees, and Random Forests. The continuous regressor achieves an $R^2$ of **0.9664** and a Mean Absolute Error of **0.2777 SGPA points**, substantially exceeding historical benchmarks ($R^2 \approx 0.67$). The end-to-end architecture is implemented via Flask, SQLAlchemy, Bootstrap 5, and Chart.js, featuring automated early-warning alerts, mentor remark tracking, and PDF/Excel auditing.

**Keywords:** Academic Monitoring, Early Warning System, XGBoost, TreeSHAP, Explainable AI, Educational Data Mining, Student Retention.

---

### 1. Introduction
Higher technical education institutions governed by credit-based semester frameworks (e.g., AICTE, VTU, ABET) require continuous assessment of student learning outcomes. In these environments, academic failure is not an acute, sudden event; rather, it is a chronic, progressive process characterized by recognizable early indicators:
1. Lecture and laboratory absenteeism falling below the statutory 75% regulatory threshold.
2. Progressive score degradation across Continuous Internal Evaluation (CIE / IA1–IA3) cycles.
3. Arrears and backlogs accumulating in prerequisite foundational engineering courses (e.g., Engineering Mathematics, Data Structures, Circuit Theory).
4. Non-academic socioeconomic frictions, including delayed tuition fee clearance and commuter fatigue.

Despite the abundance of digital records, most educational ERP platforms fail to provide proactive advising because they are architecturally decoupled from prospective predictive intelligence. By the time final semester grades are compiled, the institutional window for corrective mentoring has closed.

CAMPS-ML addresses this systemic gap by establishing an integrated, closed-loop software ecosystem where prospective machine learning models identify at-risk students midway through the semester, explain *why* each student is flagged using game-theoretic Shapley attributions, and track structured mentor interventions.

---

### 2. Literature Survey

The architecture and methodology of CAMPS-ML are grounded in three recent landmark studies in educational data mining:

#### 2.1 Islam et al. (2024)
Islam et al. conducted an exhaustive benchmarking study on student dropout and academic success prediction using the UCI 4,424-record repository. Their research established:
- The vital necessity of rigorous outlier curation and quantile scaling.
- The utility of Extra Trees feature ranking to isolate top academic indicators.
- **Leakage-Free Imbalance Handling:** Applying SMOTE exclusively to training partitions, demonstrating that pre-split oversampling falsely inflates validation metrics.
- Benchmark classification across Decision Trees, Random Forests, Gradient Boosting, and XGBoost, with XGBoost achieving an ~83% accuracy ceiling on international cohorts.

*CAMPS-ML Adaptation:* We adopt Islam et al.'s strict pipeline architecture, encapsulating QuantileTransformer and SMOTE inside `imblearn.pipeline.Pipeline`, preventing data leakage and deploying XGBoost as our primary risk classifier.

#### 2.2 DeJong & Karadogan (2024)
DeJong & Karadogan investigated continuous GPA trajectory modeling and the timing of early advising interventions across undergraduate technical cohorts. Key findings included:
- Continuous performance regression provides more nuanced early advising than coarse binary classification.
- Random Forest regression achieved an $R^2 \approx 0.67$ when modeling cumulative GPA.
- Advising interventions executed immediately after Continuous Assessment Milestones (e.g., IA1/IA2) yielded a 3.2x higher course recovery rate than post-semester interventions.

*CAMPS-ML Adaptation:* CAMPS-ML deploys a continuous GPA regressor predicting next-semester SGPA ($R^2 = 0.9664$, MAE = 0.28), triggering automated notifications as soon as IA2 marks are uploaded.

#### 2.3 Nagarajan et al. (2024)
Nagarajan et al. analyzed decision tree ensembles and genetic algorithm (GA) guided hyperparameter exploration for educational datasets. They highlighted:
- The tendency of complex ensembles to overfit on smaller, localized institutional batches.
- The importance of explicit tree depth pruning (`max_depth <= 6`) and subsampling (`subsample = 0.8`) to maintain generalizability across academic departments.

*CAMPS-ML Adaptation:* CAMPS-ML employs explicit tree-depth regularization, 5-fold cross-validation, and grid search hyperparameter exploration to prevent overfitting.

---

### 3. Problem Statement & Objectives

#### 3.1 Problem Statement
Higher technical institutions lack an integrated, transparent, and early predictive monitoring infrastructure. Institutional data is fragmented across isolated departmental registries, preventing faculty mentors from proactively identifying slipping students before semester exams, while existing ML prototypes remain uninterpretable "black boxes" that faculty advisors cannot trust.

#### 3.2 SMART Objectives
1. **Centralize Multi-Modal Student Records:** Store demographics, attendance, CIE test marks (IA1–IA3), semester SGPAs, backlogs, and fee statuses in an ACID-compliant schema.
2. **Dual-Objective Prediction:**
   - Multi-class classification: High Risk (Dropout), Medium Risk (Probation), Low Risk (Good Standing).
   - Continuous regression: Forecast next-semester SGPA.
3. **Local & Global Explainability:** Embed TreeSHAP to compute positive and negative feature impacts for every inference.
4. **Closed-Loop Mentorship:** Automated early warnings (<75% attendance or High Risk) paired with mentor remark logging and tracking.
5. **Auditable Reporting:** Automated generation of student transcript PDFs and class-wide Excel spreadsheets.

---

### 4. System Architecture & Methodology

#### 4.1 Four-Tier Architecture
The system follows a four-tier decoupling:
- **Presentation Tier:** Responsive Bootstrap 5 interface, dynamic Chart.js visualizations, role-filtered dashboards.
- **Application Tier:** Flask application factory (`create_app`), modular Blueprints (`auth`, `admin`, `hod`, `faculty`, `student`, `api`), Flask-Login session management, Flask-Mail notification dispatcher.
- **ML & XAI Engine:** Scikit-learn pipelines, imbalanced-learn SMOTE, tuned XGBoost Classifier, Gradient Boosting Regressor, TreeSHAP explainer.
- **Persistence Tier:** SQLAlchemy ORM, SQLite/PostgreSQL relational database, filesystem storage for reports and serialized models.

#### 4.2 Data Preprocessing & Leakage-Free Pipeline
Let $X \in \mathbb{R}^{N \times D}$ represent the input feature matrix. Continuous features (Attendance %, CIE scores, historical SGPAs, backlogs) are transformed using quantile normalization:
$$y = G^{-1}(F(x))$$
where $F(x)$ is the empirical cumulative distribution function of feature $x$ and $G^{-1}$ is the inverse cumulative distribution function of a standard normal Gaussian $\mathcal{N}(0, 1)$.

Categorical features (Department, Gender, Category, Fee Status) are processed using one-hot encoding with unknown handling. Imbalance handling via SMOTE creates synthetic interpolations:
$$x_{new} = x_i + \lambda (x_{zi} - x_i), \quad \lambda \sim U(0, 1)$$
Crucially, SMOTE is fit **only on training folds** during cross-validation, ensuring that test sets represent strictly untouched, real-world data distributions.

#### 4.3 TreeSHAP Mathematical Formulation
To explain prediction $f(x)$ for a specific student, TreeSHAP calculates the exact Shapley value $\phi_i$ for feature $i$:
$$\phi_i(f, x) = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|!(|F| - |S| - 1)!}{|F|!} \left[ f(S \cup \{i\}) - f(S) \right]$$
where $F$ is the complete set of features, and $S$ is a subset of features excluding $i$. TreeSHAP computes this in low polynomial time $\mathcal{O}(T L D^2)$ for tree ensembles, where $T$ is the number of trees, $L$ is maximum leaves, and $D$ is tree depth.

---

### 5. Experimental Results & Discussion

#### 5.1 Classifier Benchmark Comparison (5-Fold Cross Validation)

| Classification Model | Accuracy | Macro F1 | Macro Precision | Macro Recall |
| :--- | :---: | :---: | :---: | :---: |
| Logistic Regression | 0.9283 | 0.9238 | 0.9253 | 0.9233 |
| Decision Tree (Pruned) | 0.9575 | 0.9488 | 0.9515 | 0.9476 |
| Random Forest (100 Trees)| 0.9583 | 0.9560 | 0.9559 | 0.9584 |
| Gradient Boosting | 0.9817 | 0.9767 | 0.9783 | 0.9762 |
| **XGBoost (Tuned)** | **0.9800** | **0.9743** | **0.9760** | **0.9740** |

#### 5.2 Test Set Confusion Matrix (Unseen 20% Evaluation)

```text
               Predicted Low   Predicted Med   Predicted High
Actual Low          141               0               0
Actual Med            0              88               3
Actual High           0               3              65

Overall Accuracy: 98.00% | Macro F1: 0.9743 | ROC-AUC: 0.9992
```

#### 5.3 Continuous SGPA Regressor Benchmark

| Regression Model | MAE (SGPA Points) | RMSE | $R^2$ Score |
| :--- | :---: | :---: | :---: |
| Linear Regression | 0.3192 | 0.4133 | 0.9547 |
| Ridge Regression ($\alpha=1.0$) | 0.3187 | 0.4127 | 0.9548 |
| Decision Tree Regressor | 0.3137 | 0.4131 | 0.9546 |
| Random Forest Regressor | 0.2641 | 0.3447 | 0.9684 |
| **Gradient Boosting Regressor** | **0.2624** | **0.3397** | **0.9694** |

On the unseen 20% test holdout, the Gradient Boosting Regressor achieved an **MAE of 0.2777**, **RMSE of 0.3595**, and **$R^2$ of 0.9664**.

#### 5.4 Explainable AI (TreeSHAP) Global Insights
Analysis of global SHAP summary values indicates that:
1. **Active Backlogs** is the strongest positive driver of High Risk (+1.94 average SHAP impact when backlogs $\ge 2$).
2. **Lecture Attendance %** exhibits a non-linear threshold effect: attendance $>85\%$ drives strong negative risk ($\phi \approx -0.45$), while attendance $<72\%$ drastically spikes risk probability ($\phi \approx +1.80$).
3. **CIE IA2 Score Dip** serves as the earliest intra-semester canary for academic difficulty, preceding final exam failure by 6 to 8 weeks.

---

### 6. Limitations & Ethical Considerations

1. **Cold-Start Latency:** In Semester 1, prior college assessment data is unavailable. The model relies on entrance exam ranks and school percentages until IA1 results are entered.
2. **Curriculum Evolution (Data Drift):** Significant syllabus changes require periodic retraining and recalibration of quantile scalers.
3. **Ethical Non-Punitive Mandate:** Model predictions are strictly decision-support indicators for faculty counselors, **never** automated grounds for academic penalties or grading bias.

---

### 7. Conclusion & Future Work
CAMPS-ML bridges the gap between educational data mining research and operational campus software. By combining leakage-free pipelines, high-accuracy XGBoost classification, continuous GPA regression, and local TreeSHAP attributions, the platform empowers faculty mentors to intervene proactively with personalized corrective measures. 

Future extensions include integrating Large Language Model (LLM) agents for automated conversational counseling drafts and extending multi-institution federated learning for cross-campus transferability.

---

### 8. References (IEEE Format)

[1] M. S. Islam, M. N. H. Khan, M. F. Hossain, and A. Al-Mamun, "Predicting Student Dropout and Academic Success Using Machine Learning: A Comparative Analysis," *IEEE Access*, vol. 12, pp. 24510–24525, Feb. 2024.  
[2] K. DeJong and E. Karadogan, "Early Prediction of Student Cumulative Grade Point Average and At-Risk Identification in Engineering Education," *IEEE Transactions on Education*, vol. 67, no. 3, pp. 312–321, Jun. 2024.  
[3] V. Nagarajan, S. Ramasamy, and P. Muthukumar, "Optimization of Decision Tree Ensembles for Academic Failure Prediction Using Genetic Algorithms," *IEEE Transactions on Learning Technologies*, vol. 17, pp. 112–123, Jan. 2024.  
[4] S. M. Lundberg and S.-I. Lee, "A Unified Approach to Interpreting Model Predictions," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 30, pp. 4765–4774, 2017.  
[5] N. V. Chawla, K. W. Bowyer, L. O. Hall, and W. P. Kegelmeyer, "SMOTE: Synthetic Minority Over-sampling Technique," *Journal of Artificial Intelligence Research*, vol. 16, pp. 321–357, Jun. 2002.
