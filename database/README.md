# Database Architecture: CAMPS-ML
## PES Institute of Technology & Management (PESITM), Shivamogga
### VTU B.E. Computer Science & Engineering Capstone Project

This directory manages the relational database persistence tier for CAMPS-ML using **MySQL 8.0**.

---

### Monorepo Database Directory Structure
```text
database/
├── README.md       # Architecture & operational instructions
├── schema.sql      # Complete DDL tables, foreign keys with ON DELETE rules, and indexes
└── seed.sql        # Realistic initial data: 1 Admin, 3 Teachers, 60 Students, 40 Parents
```

---

### Core Relational Entities
1. **users:** Authentication credentials, role-based access (`admin`, `teacher`, `student`, `parent`), active status, timestamps.
2. **students:** Student academic profile, USN, class reference, parent reference, academic status.
3. **teachers:** Faculty profiles, employee designation, department reference.
4. **parents:** Guardian profiles, relation type, emergency contact.
5. **classes:** Academic classes, sections (A/B), academic years, department references.
6. **subjects:** Curriculum subjects, semester mappings, credits, assigned teacher.
7. **attendance:** Daily and aggregate attendance tracking per subject.
8. **marks:** Continuous internal evaluation (IA1-3, assignments, quizzes, final CIE).
9. **participation:** Extra-curricular and classroom engagement scores per subject.
10. **semester_results:** Historical SGPA and cumulative CGPA records.
11. **predictions:** Machine learning inference logs (Pass/Fail, risk level, confidence score, model version).
12. **explanations:** TreeSHAP feature attributions per prediction.
13. **alerts:** Early-warning risk notifications for teachers and parents.
14. **remarks:** Faculty counselling notes and intervention records.
15. **notifications:** In-app user notifications.
16. **model_runs:** Training run metadata, accuracy, precision, recall, and macro-F1 logs.

---

### Local MySQL Setup (Quick Commands)
```bash
# Log in to MySQL CLI
mysql -u root -p

# Create database and grant privileges
CREATE DATABASE camps_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Apply schema & seed data
mysql -u root -p camps_db < database/schema.sql
mysql -u root -p camps_db < database/seed.sql
```
