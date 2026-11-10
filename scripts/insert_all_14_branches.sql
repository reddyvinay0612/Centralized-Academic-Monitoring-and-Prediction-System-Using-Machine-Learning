-- ==============================================================================
-- PESITM SHIVAMOGGA - Insert All 14 Academic Departments into camps_db
-- 10 Engineering Disciplines + 4 Basic Sciences & Humanities
-- Run this in phpMyAdmin -> SQL tab
-- ==============================================================================

USE camps_db;

INSERT INTO `departments` (`dept_id`, `dept_code`, `name`, `hod_teacher_id`, `created_at`) VALUES
(1, 'CSE', 'Computer Science and Engineering', 1, NOW()),
(2, 'ISE', 'Information Science and Engineering', 2, NOW()),
(3, 'ECE', 'Electronics and Communications Engineering', 3, NOW()),
(4, 'CSD', 'Computer Science and Design', 4, NOW()),
(5, 'CIV', 'Civil Engineering', NULL, NOW()),
(6, 'EEE', 'Electrical and Electronics Engineering', NULL, NOW()),
(7, 'MECH', 'Mechanical Engineering', NULL, NOW()),
(8, 'AIML', 'Artificial Intelligence and Machine Learning', NULL, NOW()),
(9, 'CE', 'Computer Engineering', NULL, NOW()),
(10, 'CSDS', 'Computer Science and Engineering(Data Science)', NULL, NOW()),
(11, 'PHY', 'Physics', NULL, NOW()),
(12, 'MATH', 'Mathematics', NULL, NOW()),
(13, 'CHEM', 'Chemistry', NULL, NOW()),
(14, 'HUM', 'Humanities', NULL, NOW())
ON DUPLICATE KEY UPDATE 
    `dept_code` = VALUES(`dept_code`),
    `name` = VALUES(`name`);

-- Verify the 14 departments
SELECT `dept_id`, `dept_code`, `name` FROM `departments` ORDER BY `dept_id`;
