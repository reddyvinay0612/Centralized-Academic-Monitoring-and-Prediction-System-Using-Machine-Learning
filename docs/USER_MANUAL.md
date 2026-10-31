# CAMPS-ML User Manual & Operational Guide

---

## 1. System Roles & Access Matrix

CAMPS-ML features 4 distinct role permissions:
1. **System Administrator:** Global system configuration, user account creation, role assignment, and bulk CSV dataset ingestion.
2. **Head of Department (HoD):** Department-wide cohort analytics, pass/fail trends, mentor tracking, and class Excel risk report exports.
3. **Faculty / Mentor:** Class-wise continuous assessment entry, mentee monitoring, deep-dive XAI risk diagnostics, and counseling remark logging.
4. **Student:** Personal academic overview, attendance tracking, SGPA historical trajectory, TreeSHAP insights, personalized AI study tips, and PDF transcript download.

---

## 2. Step-by-Step Role Walkthroughs

### 2.1 Administrator Workflows
- **Signing In:** Navigate to `/auth/login` and enter administrator credentials (`admin@camps.edu` / `Admin@123`).
- **Reviewing System Overview:** The `/admin/dashboard` displays active counts of students, faculty, critical risk count, and live ML model statuses.
- **Bulk Data Ingestion:**
  1. Click **Bulk Data Upload** in the sidebar.
  2. Select the Department and target semester (e.g., CSD, Semester 5).
  3. Attach the CSV/Excel file and click **Start Ingestion & Trigger ML**.
  4. The system validates the schema, commits the records, and runs real-time inference on all uploaded students.

### 2.2 HoD Workflows
- **Signing In:** Use `hod.csd@camps.edu` / `Hod@123`.
- **Department Risk Oversight:** View the donut breakdown of Low, Medium, and High-risk students.
- **Exporting Reports:** Click **Download Class Excel Audit Sheet** to download a formatted `.xlsx` workbook containing complete student metrics.

### 2.3 Faculty / Mentor Workflows
- **Signing In:** Use `prof.anita@camps.edu` / `Faculty@123`.
- **Filtering Mentees:** Use the top filter buttons (`High Risk`, `Medium Risk`, `Good Standing`) to identify mentees who need attention.
- **Inspecting a Mentee:**
  1. Click **Inspect** on any mentee row.
  2. Review the **TreeSHAP Feature Attributions** showing positive and negative drivers of risk.
  3. Inspect the course-wise attendance percentages (shortages highlighted in red).
  4. Enter notes in the **Log Mentor Counselling & Action Plan** form, choose a follow-up timeframe (e.g., 14 days), and click **Save Intervention**.
  5. Click **Download PDF Transcript** to generate the official student record.

### 2.4 Student Workflows
- **Signing In:** Use `student.1rv21cd001@camps.edu` / `Student@123`.
- **Reviewing SGPA Trajectory:** View the interactive Chart.js graph displaying past semester SGPAs and the ML forecasted target for the current semester.
- **Actioning AI Advice:** Read the personalized improvement suggestions (e.g., remedial lab makeup, backlog coaching).
- **Downloading Transcript:** Click **Download PDF** to obtain an official academic transcript.
