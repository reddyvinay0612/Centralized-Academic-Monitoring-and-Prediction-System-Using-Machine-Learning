# CAMPS-ML: Capstone Presentation Slide Deck Outline
## 12-Slide Structure for Final Evaluation Review

---

### Slide 1: Title & Presentation Header
- **Project Title:** Centralized Academic Monitoring and Prediction System Using Machine Learning (CAMPS-ML)
- **Candidate Name:** Final-Year B.E. (Computer Science and Design)
- **Guide / Mentors:** Department of Computer Science and Design
- **Institutional Emblem & Academic Year:** 2024–2025

---

### Slide 2: The Core Problem & Motivation
- **The Challenge:** Progressive academic failure, backlogs, and dropouts in credit-based engineering curricula.
- **The Gap:** Existing institutional software acts purely as retrospective audit logs (recording grades after semester finals).
- **The "Black Box" Barrier:** Existing ML academic research rarely translates to operational dashboards and lacks explainability for faculty.

---

### Slide 3: SMART Objectives & Scope
- **Objective 1:** Centralize multi-modal academic records (demographics, CIE IA1–IA3, attendance %, backlogs, fee dues).
- **Objective 2:** Dual ML modeling: 3-class risk classification + continuous next-semester SGPA regression.
- **Objective 3:** Implement TreeSHAP for per-student local feature attributions.
- **Objective 4:** Closed-loop early warnings (<75% attendance alert) and mentor remark tracking.
- **Objective 5:** Automated PDF transcripts and Excel audit sheets.

---

### Slide 4: Literature Survey & Research Methodology
- **Islam et al. (2024):** Leakage-free SMOTE on training split only; Extra Trees ranking; XGBoost classification benchmark (~83%).
- **DeJong & Karadogan (2024):** Continuous GPA regression ($R^2 \approx 0.67$); early advising after internal assessment milestones.
- **Nagarajan et al. (2024):** Decision tree ensemble regularization and overfitting mitigation.

---

### Slide 5: System Architecture & Workflow
- *Embed Mermaid 4-Tier Architecture Diagram:*
  - Presentation Tier (Bootstrap 5, Chart.js)
  - Application Tier (Flask Factory, RBAC, Services)
  - ML & XAI Engine (XGBoost, Gradient Boosting, TreeSHAP)
  - Persistence Tier (SQLAlchemy, SQLite/PostgreSQL)

---

### Slide 6: Machine Learning Pipeline & Leakage-Free Design
- Preprocessing: Quantile Transformer for skewed continuous variables, OneHotEncoder for categoricals.
- Imbalance Handling: SMOTE strictly fit on training partitions via `imblearn.pipeline.Pipeline`.
- Hyperparameter Tuning: GridSearchCV across tree depth, learning rate, and subsampling ratios.

---

### Slide 7: Model Comparison & Benchmark Results
- *Bar Chart & Table showing 5-Fold Cross Validation:*
  - Logistic Regression: 92.8%
  - Decision Tree: 95.8%
  - Random Forest: 95.8%
  - Gradient Boosting: 98.2%
  - **Tuned XGBoost: 98.0% Accuracy | 0.9743 Macro-F1 | 0.9992 ROC-AUC**
- Continuous SGPA Regressor: **$R^2 = 0.9664$, MAE = 0.2777 SGPA points**.

---

### Slide 8: Explainable AI (XAI) with TreeSHAP
- Why TreeSHAP? Game-theoretic Shapley values satisfying local accuracy and consistency.
- Global Summary Plot: Identifying department-wide risk drivers (Active Backlogs, Attendance %, CIE IA2).
- Local Waterfall Plot: Pinpointing why *Student X* was flagged and translating SHAP values into automated study recommendations.

---

### Slide 9: Role-Based System Features & UI Walkthrough
- **Admin:** System overview, user management, drag-and-drop CSV batch upload.
- **HoD:** Departmental risk analytics, class Excel audit export.
- **Faculty:** Mentee monitoring, attendance shortage tags, student diagnostic profile, intervention logging.
- **Student:** Interactive SGPA trajectory chart, TreeSHAP insights, personalized AI tips, PDF transcript download.

---

### Slide 10: Testing & Quality Assurance
- Automated Pytest Suite: 9 tests passing with 100% pass rate in 6.12s.
- Test coverage across ORM models, ML pipeline boundaries, and route RBAC access control.
- Dockerized deployment setup (`Dockerfile`, `docker-compose.yml`, `render.yaml`).

---

### Slide 11: Limitations, Ethics & Defense Notes
- Non-Punitive Mandate: Decision-support tool for mentors, never automated punitive sanctions.
- Cold-Start Solution: Entrance exam and school metrics for first 4 weeks until IA1 is recorded.
- Curriculum Drift Handling: Modular script-based retraining in seconds.

---

### Slide 12: Conclusion & Future Scope
- **Conclusion:** CAMPS-ML successfully transforms static institutional data into a proactive, transparent early-warning system.
- **Future Scope:** LLM agent conversational counseling drafts, mobile application push notifications, and cross-university federated learning.
- **Q&A:** "Thank you. We invite questions from the committee."
