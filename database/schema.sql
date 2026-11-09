-- =====================================================================
-- Centralized Academic Monitoring and Prediction System (CAMPS-ML)
-- Institution: PES Institute of Technology & Management, Shivamogga (VTU)
-- Multi-Role Security & Scoped Governance Database Schema
-- Roles: student, parent, teacher, hod, principal, admin
-- =====================================================================

CREATE DATABASE IF NOT EXISTS camps_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE camps_db;

SET FOREIGN_KEY_CHECKS = 0;

-- Drop all existing tables for a clean, deterministic initialization
DROP TABLE IF EXISTS mark_history;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS audit_log;
DROP TABLE IF EXISTS refresh_tokens;
DROP TABLE IF EXISTS password_resets;
DROP TABLE IF EXISTS remarks;
DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS explanations;
DROP TABLE IF EXISTS predictions;
DROP TABLE IF EXISTS model_runs;
DROP TABLE IF EXISTS semester_results;
DROP TABLE IF EXISTS participation;
DROP TABLE IF EXISTS marks;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS fee_payments;
DROP TABLE IF EXISTS fees;
DROP TABLE IF EXISTS timetable;
DROP TABLE IF EXISTS teacher_classes;
DROP TABLE IF EXISTS parent_students;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS classes;
DROP TABLE IF EXISTS parents;
DROP TABLE IF EXISTS teachers;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS users;

-- ---------------------------------------------------------------------
-- 1. USERS (Central RBAC Credentials, Rate-limiting & Account Security)
-- ---------------------------------------------------------------------
CREATE TABLE users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(60) NOT NULL UNIQUE,
  email VARCHAR(100) NOT NULL UNIQUE,
  phone VARCHAR(20) NULL,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('student', 'parent', 'teacher', 'hod', 'principal', 'admin') NOT NULL,
  active BOOLEAN DEFAULT TRUE,
  must_change_password BOOLEAN DEFAULT FALSE,
  failed_attempts INT DEFAULT 0,
  locked_until TIMESTAMP NULL,
  last_login TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_users_role (role),
  INDEX idx_users_email (email),
  INDEX idx_users_username (username)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 2. DEPARTMENTS (Academic Branches with HoD Mapping)
-- ---------------------------------------------------------------------
CREATE TABLE departments (
  dept_id INT AUTO_INCREMENT PRIMARY KEY,
  dept_code VARCHAR(10) NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  hod_teacher_id INT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_departments_code (dept_code)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 3. TEACHERS (Faculty, Mentors, and HoDs)
-- ---------------------------------------------------------------------
CREATE TABLE teachers (
  teacher_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  employee_id VARCHAR(20) NOT NULL UNIQUE,
  designation VARCHAR(60) DEFAULT 'Assistant Professor',
  dept_id INT NOT NULL,
  phone VARCHAR(20),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE RESTRICT,
  INDEX idx_teachers_emp_id (employee_id),
  INDEX idx_teachers_dept (dept_id)
) ENGINE=InnoDB;

-- Add deferred foreign key from departments to teachers for HoD mapping
ALTER TABLE departments
  ADD CONSTRAINT fk_dept_hod FOREIGN KEY (hod_teacher_id) REFERENCES teachers(teacher_id) ON DELETE SET NULL;

-- ---------------------------------------------------------------------
-- 4. PARENTS / GUARDIANS
-- ---------------------------------------------------------------------
CREATE TABLE parents (
  parent_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  phone VARCHAR(20) NOT NULL,
  email VARCHAR(100),
  address TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  INDEX idx_parents_phone (phone)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 5. CLASSES (Semesters and Cohort Sections)
-- ---------------------------------------------------------------------
CREATE TABLE classes (
  class_id INT AUTO_INCREMENT PRIMARY KEY,
  class_name VARCHAR(50) NOT NULL,
  section VARCHAR(5) NOT NULL,
  semester INT NOT NULL,
  academic_year VARCHAR(15) NOT NULL,
  dept_id INT NOT NULL,
  mentor_teacher_id INT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_class_sec_year (class_name, section, academic_year),
  FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE RESTRICT,
  FOREIGN KEY (mentor_teacher_id) REFERENCES teachers(teacher_id) ON DELETE SET NULL,
  INDEX idx_classes_dept (dept_id),
  INDEX idx_classes_semester (semester)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 6. SUBJECTS (Course Curriculum)
-- ---------------------------------------------------------------------
CREATE TABLE subjects (
  subject_id INT AUTO_INCREMENT PRIMARY KEY,
  subject_code VARCHAR(15) NOT NULL UNIQUE,
  subject_name VARCHAR(100) NOT NULL,
  semester INT NOT NULL,
  credits INT NOT NULL DEFAULT 3,
  dept_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE RESTRICT,
  INDEX idx_subjects_sem (semester),
  INDEX idx_subjects_dept (dept_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 7. STUDENTS (Academic Registry & Enrollment)
-- ---------------------------------------------------------------------
CREATE TABLE students (
  student_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  usn VARCHAR(20) NOT NULL UNIQUE,
  class_id INT NOT NULL,
  academic_status ENUM('active', 'detained', 'graduated', 'dropped') DEFAULT 'active',
  fee_status ENUM('paid', 'pending') DEFAULT 'paid',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE RESTRICT,
  INDEX idx_students_usn (usn),
  INDEX idx_students_class (class_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 8. PARENT_STUDENTS (Many-to-Many Linking: One Parent -> Multiple Children)
-- ---------------------------------------------------------------------
CREATE TABLE parent_students (
  parent_id INT NOT NULL,
  student_id INT NOT NULL,
  relation VARCHAR(50) DEFAULT 'Parent',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (parent_id, student_id),
  FOREIGN KEY (parent_id) REFERENCES parents(parent_id) ON DELETE CASCADE,
  FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
  INDEX idx_parent_students_student (student_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 9. TEACHER_CLASSES (Class & Subject Assignments for Scoped Access)
-- ---------------------------------------------------------------------
CREATE TABLE teacher_classes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  teacher_id INT NOT NULL,
  class_id INT NOT NULL,
  subject_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_teacher_class_subject (teacher_id, class_id, subject_id),
  FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE,
  FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
  FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
  INDEX idx_tc_teacher (teacher_id),
  INDEX idx_tc_class (class_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 10. TIMETABLE (Weekly Classroom Lecture & Lab Schedules)
-- ---------------------------------------------------------------------
CREATE TABLE timetable (
  timetable_id INT AUTO_INCREMENT PRIMARY KEY,
  class_id INT NOT NULL,
  subject_id INT NOT NULL,
  teacher_id INT NULL,
  day_of_week VARCHAR(15) NOT NULL,
  start_time VARCHAR(10) NOT NULL,
  end_time VARCHAR(10) NOT NULL,
  room_number VARCHAR(20) NOT NULL DEFAULT 'LH-101',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
  FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
  FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE SET NULL,
  INDEX idx_timetable_class (class_id),
  INDEX idx_timetable_day (day_of_week)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 11. FEES (Annual Institutional Tuition & Fee Structure per Class)
-- ---------------------------------------------------------------------
CREATE TABLE fees (
  fee_id INT AUTO_INCREMENT PRIMARY KEY,
  class_id INT NOT NULL,
  academic_year VARCHAR(15) NOT NULL,
  total_amount DECIMAL(10,2) NOT NULL,
  due_date DATETIME NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
  INDEX idx_fees_class (class_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 12. FEE_PAYMENTS (Student Transaction & Receipt Ledger)
-- ---------------------------------------------------------------------
CREATE TABLE fee_payments (
  payment_id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  amount_paid DECIMAL(10,2) NOT NULL,
  payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  payment_mode VARCHAR(50) DEFAULT 'Online/UPI' NOT NULL,
  transaction_reference VARCHAR(100) NOT NULL UNIQUE,
  status ENUM('completed', 'pending', 'failed') DEFAULT 'completed' NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
  INDEX idx_fee_payments_student (student_id),
  INDEX idx_fee_payments_status (status)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 13. ATTENDANCE (Aggregated Subject Attendance Logs)
-- ---------------------------------------------------------------------
CREATE TABLE attendance (
  attendance_id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  subject_id INT NOT NULL,
  total_classes INT NOT NULL DEFAULT 0,
  attended_classes INT NOT NULL DEFAULT 0,
  percentage DECIMAL(5,2) GENERATED ALWAYS AS (
    CASE WHEN total_classes > 0 THEN (attended_classes / total_classes) * 100 ELSE 0.0 END
  ) STORED,
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_student_subject_att (student_id, subject_id),
  FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
  FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
  INDEX idx_attendance_percentage (percentage)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 11. MARKS (Continuous Internal Evaluation Assessment Marks)
-- ---------------------------------------------------------------------
CREATE TABLE marks (
  marks_id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  subject_id INT NOT NULL,
  cie1 DECIMAL(4,1) DEFAULT 0.0,
  cie2 DECIMAL(4,1) DEFAULT 0.0,
  cie3 DECIMAL(4,1) DEFAULT 0.0,
  assignment_marks DECIMAL(4,1) DEFAULT 0.0,
  quiz_marks DECIMAL(4,1) DEFAULT 0.0,
  total_cie DECIMAL(5,2) DEFAULT 0.0,
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_student_subject_marks (student_id, subject_id),
  FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
  FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
  INDEX idx_marks_student (student_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 12. MARK_HISTORY (Audited Trail of Grade Alterations)
-- ---------------------------------------------------------------------
CREATE TABLE mark_history (
  id INT AUTO_INCREMENT PRIMARY KEY,
  marks_id INT NOT NULL,
  field_name VARCHAR(50) NOT NULL DEFAULT 'total_cie',
  old_value DECIMAL(5,2) NOT NULL,
  new_value DECIMAL(5,2) NOT NULL,
  changed_by INT NOT NULL,
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  reason TEXT NOT NULL,
  FOREIGN KEY (marks_id) REFERENCES marks(marks_id) ON DELETE CASCADE,
  FOREIGN KEY (changed_by) REFERENCES users(user_id) ON DELETE RESTRICT,
  INDEX idx_mark_history_marks (marks_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 13. PARTICIPATION (Lab & Classroom Engagement)
-- ---------------------------------------------------------------------
CREATE TABLE participation (
  participation_id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  subject_id INT NOT NULL,
  score DECIMAL(4,1) NOT NULL DEFAULT 5.0,
  month VARCHAR(15) NOT NULL,
  remarks VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
  FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 14. SEMESTER_RESULTS (Historical SGPA & Cumulative Performance)
-- ---------------------------------------------------------------------
CREATE TABLE semester_results (
  result_id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  semester INT NOT NULL,
  sgpa DECIMAL(4,2) NOT NULL,
  credits_earned INT NOT NULL DEFAULT 20,
  backlogs INT NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_student_semester (student_id, semester),
  FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
  INDEX idx_semester_sgpa (sgpa)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 15. MODEL_RUNS (Machine Learning Models & Evaluation Metrics)
-- ---------------------------------------------------------------------
CREATE TABLE model_runs (
  run_id INT AUTO_INCREMENT PRIMARY KEY,
  model_name VARCHAR(100) NOT NULL,
  model_version VARCHAR(20) NOT NULL,
  algorithm VARCHAR(100) NOT NULL,
  accuracy DECIMAL(5,4) NOT NULL,
  precision_macro DECIMAL(5,4) NOT NULL,
  recall_macro DECIMAL(5,4) NOT NULL,
  f1_macro DECIMAL(5,4) NOT NULL,
  roc_auc DECIMAL(5,4) NOT NULL,
  regressor_r2 DECIMAL(5,4) NOT NULL,
  trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  metrics_json JSON,
  INDEX idx_model_version (model_version)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 16. PREDICTIONS (XGBoost Inferences & Predicted Risk)
-- ---------------------------------------------------------------------
CREATE TABLE predictions (
  prediction_id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  model_run_id INT NOT NULL,
  predicted_outcome ENUM('Pass', 'Fail', 'Dropout', 'Graduate') NOT NULL,
  risk_score DECIMAL(5,4) NOT NULL,
  risk_level ENUM('low', 'medium', 'high') NOT NULL,
  predicted_sgpa DECIMAL(4,2),
  generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
  FOREIGN KEY (model_run_id) REFERENCES model_runs(run_id) ON DELETE RESTRICT,
  INDEX idx_predictions_risk_level (risk_level),
  INDEX idx_predictions_score (risk_score)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 17. EXPLANATIONS (TreeSHAP Attributions)
-- ---------------------------------------------------------------------
CREATE TABLE explanations (
  explanation_id INT AUTO_INCREMENT PRIMARY KEY,
  prediction_id INT NOT NULL,
  feature_name VARCHAR(100) NOT NULL,
  feature_value VARCHAR(50) NOT NULL,
  shap_value DECIMAL(6,4) NOT NULL,
  rank_order INT NOT NULL DEFAULT 1,
  FOREIGN KEY (prediction_id) REFERENCES predictions(prediction_id) ON DELETE CASCADE,
  INDEX idx_explanations_prediction (prediction_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 18. ALERTS (Regulatory & Academic Risk Warnings)
-- ---------------------------------------------------------------------
CREATE TABLE alerts (
  alert_id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  risk_level ENUM('medium', 'high') NOT NULL,
  reason TEXT NOT NULL,
  status ENUM('open', 'contacted', 'resolved') DEFAULT 'open',
  email_sent BOOLEAN DEFAULT FALSE,
  sms_sent BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  resolved_at TIMESTAMP NULL,
  FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
  INDEX idx_alerts_status (status)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 19. REMARKS (Faculty Counseling & Mentorship Interventions)
-- ---------------------------------------------------------------------
CREATE TABLE remarks (
  remark_id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  teacher_id INT NOT NULL,
  remark_text TEXT NOT NULL,
  action_taken TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
  FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 20. PASSWORD_RESETS (Single-use Cryptographic Reset Tokens)
-- ---------------------------------------------------------------------
CREATE TABLE password_resets (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  token_hash VARCHAR(255) NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  used BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  INDEX idx_pwd_resets_token (token_hash)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 21. REFRESH_TOKENS (HttpOnly Secure Cookie Refresh Token Store)
-- ---------------------------------------------------------------------
CREATE TABLE refresh_tokens (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  token_hash VARCHAR(255) NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  revoked BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  INDEX idx_refresh_tokens_hash (token_hash)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 22. AUDIT_LOG (Immutable Administrative & Security Event Record)
-- ---------------------------------------------------------------------
CREATE TABLE audit_log (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NULL,
  role VARCHAR(20) NULL,
  action VARCHAR(100) NOT NULL,
  target_type VARCHAR(50) NULL,
  target_id INT NULL,
  ip VARCHAR(50) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
  INDEX idx_audit_action (action),
  INDEX idx_audit_user (user_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 23. NOTIFICATIONS (In-app, SMS, & Email Multi-channel Notifications)
-- ---------------------------------------------------------------------
CREATE TABLE notifications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sender_id INT NULL,
  recipient_user_id INT NOT NULL,
  student_id INT NULL,
  title VARCHAR(150) NOT NULL,
  message TEXT NOT NULL,
  channel ENUM('in_app', 'email', 'sms') DEFAULT 'in_app',
  status ENUM('pending', 'sent', 'read') DEFAULT 'sent',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  read_at TIMESTAMP NULL,
  FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE SET NULL,
  FOREIGN KEY (recipient_user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE SET NULL,
  INDEX idx_notif_recipient (recipient_user_id),
  INDEX idx_notif_status (status)
) ENGINE=InnoDB;

SET FOREIGN_KEY_CHECKS = 1;
