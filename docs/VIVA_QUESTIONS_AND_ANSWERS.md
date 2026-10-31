# CAMPS-ML: Capstone Viva Defense Guide
## 25 Questions & Bulletproof Engineering Answers

---

### Machine Learning & Data Science

#### Q1: Why did you choose XGBoost as your primary classifier over Deep Learning or simple Decision Trees?
**Answer:** Academic tabular datasets are heterogeneous, containing mixed numerical and categorical features with non-linear threshold effects (e.g., <75% attendance rule). XGBoost consistently outperforms deep neural networks on structured tabular data of this scale (~1,500 to 5,000 rows). Unlike single Decision Trees which easily overfit, XGBoost uses gradient boosted trees with L1/L2 leaf regularization (`reg_alpha`, `reg_lambda`), column subsampling, and shrinkage learning rates to prevent overfitting.

#### Q2: What is Data Leakage, and how did you prevent it in your ML pipeline?
**Answer:** Data leakage occurs when information from outside the training dataset (such as test fold distributions or global target proportions) leaks into model training. For example, fitting a scaler or applying SMOTE on the whole dataset *before* cross-validation splits leaks test distribution into the train set, giving falsely high validation scores. We prevented this by encapsulating all transformations (QuantileTransformer, SimpleImputer, and SMOTE) inside an `imblearn.pipeline.Pipeline`, which strictly fits transformations only on the training split during 5-fold CV.

#### Q3: Why use both Classification and Regression models? Why not just one?
**Answer:** They serve complementary advising functions (as shown by DeJong & Karadogan 2024):
- **Classification (XGBoost):** Flags the categorical risk severity tier (High, Medium, Low) for department-level triaging and automated early warning alerts.
- **Regression (Gradient Boosting):** Provides a continuous forecast of next-semester SGPA (e.g. 6.45). This gives students an achievable numerical milestone and shows mentors the exact rate of improvement or decline.

#### Q4: Why did you use TreeSHAP instead of LIME or standard feature importance?
**Answer:** Standard feature importance (MDI) only shows global importance and suffers from bias towards high-cardinality features. LIME uses local linear perturbations which are slow and non-deterministic (different runs can give different explanations). **TreeSHAP** is mathematically exact for tree ensembles based on game-theoretic Shapley values, satisfying three fundamental axioms: *Local Accuracy*, *Missingness*, and *Consistency*. It provides exact per-student feature attributions in polynomial time.

#### Q5: How did you handle class imbalance in your target variable?
**Answer:** In educational datasets, failing/dropout students are typically the minority class (~20-25%). We used **SMOTE (Synthetic Minority Over-sampling Technique)** on the training fold to generate synthetic interpolated samples for minority classes, combined with evaluating models using **Macro-F1** and **ROC-AUC (One-vs-Rest)** rather than misleading raw accuracy.

#### Q6: What were the top 3 features driving high academic risk in TreeSHAP?
**Answer:**
1. **Active Backlogs / Arrears:** Having $\ge 2$ uncleared prerequisite courses.
2. **Lecture Attendance %:** Attendance dipping below the mandatory 75% threshold.
3. **Continuous Internal Evaluation (CIE IA2 Score):** Mid-semester assessment drop serving as an early canary 6-8 weeks before final examinations.

#### Q7: How do you handle the "Cold-Start" problem for 1st-semester students?
**Answer:** First-semester students have no prior college exam history. During the first 4 weeks, the system utilizes prior secondary school percentages (10th/12th), entrance exam rank, and initial attendance. Once Continuous Assessment 1 (IA1) marks are recorded at week 6, the model updates and predictive confidence rises significantly.

---

### Software Engineering & Full-Stack Architecture

#### Q8: Why did you choose Flask and the Application Factory Pattern instead of Django or a single `app.py`?
**Answer:** Flask is lightweight, modular, and does not impose rigid ORM or admin constraints. The **Application Factory Pattern** (`create_app()`) allows us to dynamically instantiate the application with different configurations (e.g., in-memory SQLite for automated Pytest unit tests, persistent SQLite for local development, and PostgreSQL/Gunicorn for production) without circular imports.

#### Q9: How is Role-Based Access Control (RBAC) enforced in your application?
**Answer:** We implemented a custom `@role_required(*allowed_roles)` Python decorator on top of Flask-Login's `@login_required`. When a user attempts to access a protected route (e.g. `/admin/dashboard`), the decorator inspects `current_user.role`. If the user does not possess authorization, the request is intercepted and redirected with an "Access Denied" flash alert.

#### Q10: How does the system handle bulk data uploads?
**Answer:** In `app/services/data_ingestion.py`, we parse uploaded CSV/Excel files using Pandas, validate required schema headers, and perform transactional batch upserts using SQLAlchemy ORM. Immediately after database commit, the service triggers on-the-fly ML scoring for every ingested student so predictions and SHAP attributions are live instantly.

#### Q11: What database indexing strategies did you employ?
**Answer:** We indexed high-frequency lookup fields: `User.email` (unique index), `StudentProfile.usn` (unique index), `Course.code` (unique index), and foreign keys (`student_id`, `department_id`, `mentor_id`) to ensure fast JOIN operations and sub-millisecond query responses.

---

### Ethics, Limitations & Real-World Viability

#### Q12: Can this ML model unfairly bias or penalize a student?
**Answer:** No. CAMPS-ML is strictly a **decision-support advisory system** for human mentors, **never** an automated punitive grading tool. Mentors use the SHAP explanations to schedule remedial counseling and academic support. Furthermore, sensitive demographic variables (gender, category) are audited to ensure fairness.

#### Q13: What happens when the curriculum changes (Data Drift)?
**Answer:** When curriculum structures or course credit distributions evolve, data drift occurs. Our modular pipeline allows running `python ml_engine/train_classifier.py` and `python ml_engine/train_regressor.py` via an administrative command to recalibrate the quantile scalers and retrain tree weights within seconds.

---

### Quick Cheat-Sheet for Numbers to Quote

- **Classification Accuracy:** 98.00% on unseen test data.
- **Classification Macro-F1:** 0.9743.
- **Classification ROC-AUC:** 0.9992.
- **Continuous SGPA Regressor $R^2$:** 0.9664 (MAE = 0.2777 SGPA points).
- **Test Suite Pass Rate:** 9/9 automated tests passing in 6.12s.
