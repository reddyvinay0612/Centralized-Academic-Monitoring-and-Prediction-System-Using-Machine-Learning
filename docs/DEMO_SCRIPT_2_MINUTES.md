# CAMPS-ML: 2-Minute Live Project Demonstration Script

**Target Time:** 120 Seconds  
**Audience:** External Examiner, Guide, Evaluation Committee  
**Setup:** Have `py run.py` running in terminal and open `http://127.0.0.1:5000` in browser.

---

### [0:00 - 0:25] Introduction & The Core Problem
*(Screen on Login Page)*
> "Respected examiners, good morning. In our technical colleges, student failure and dropouts rarely happen overnight. They happen gradually: attendance dips below 75%, internal marks slide, and backlogs pile up. 
> Traditional college portals only calculate marks after final exams—when it is already too late.
> Today, I am presenting **CAMPS-ML**: an end-to-end Academic Monitoring and Early-Warning Web Platform powered by Machine Learning and Explainable AI."

---

### [0:25 - 0:50] Admin & HoD Big-Picture Monitoring
*(Action: Click 1-click button "HoD" -> Signs in as Dr. Ramesh)*
> "Let's first log in as the **Head of Department**. 
> Instantly, the HoD sees departmental KPIs: cohort risk distribution, department average CGPA (6.84), and a prioritized list of students classified as **High Risk** by our tuned **XGBoost model** which achieved **98% accuracy and 0.97 F1 score**.
> With one click on 'Export Class Audit', the HoD can download an accreditation-ready Excel audit sheet containing attendance, backlogs, and projected GPAs for every student."

---

### [0:50 - 1:20] Faculty Mentorship & Explainable AI (TreeSHAP)
*(Action: Click "Inspect" next to Rohan Verma (1RV21CD001))*
> "Now let's step into the role of a **Faculty Mentor**. Mentors don't just need a risk label; they need to know *why* a student is slipping.
> Here is the diagnostic screen for Rohan Verma.
> Our system uses **TreeSHAP** from game theory to break down the exact positive and negative drivers of risk. We can see Rohan has a 100% risk probability because his active backlogs contribute +1.94 to risk, and his attendance is down at 57.5%.
> The mentor immediately types a counseling remark: 'Scheduled two remedial lab sessions on Saturday', sets a 14-day follow-up review, and saves it to the permanent audit trail."

---

### [1:20 - 1:45] Student Self-Advising & PDF Transcript
*(Action: Log out -> Click 1-click button "Student (High Risk)" -> Signs in as Rohan)*
> "Finally, let's view the portal from the **Student's perspective**. 
> Rohan logs in and sees his interactive SGPA trajectory chart, including our **Gradient Boosting Regressor's forecasted next-semester SGPA** (R² = 0.966).
> Below, the system delivers personalized AI improvement suggestions generated directly from his SHAP values: notifying him to complete compensatory lab makeup sessions and enroll in supplementary coaching.
> He can click 'Download PDF' to instantly generate a branded, confidential transcript report ready for parent-teacher review."

---

### [1:45 - 2:00] Conclusion & Technical Rigor
*(Screen showing terminal with `pytest` passing 9/9)*
> "Behind the scenes, all models are trained strictly with leakage-free pipelines and SMOTE on training splits only, verified by a full automated test suite passing 100%.
> CAMPS-ML transforms educational data from a passive historical archive into an active, life-saving early warning system. Thank you, and I welcome your questions."
