/**
 * Application Constants & Role Definitions
 */

export const ROLES = {
  ADMIN: 'admin',
  HOD: 'hod',
  FACULTY: 'faculty',
  STUDENT: 'student',
};

export const ROUTES = {
  LOGIN: '/login',
  OVERVIEW: '/overview',
  STUDENTS: '/students',
  STUDENT_DETAIL: '/students/:id',
  ALERTS: '/alerts',
  UPLOAD: '/upload',
  MY_PROGRESS: '/me',
  ADMIN: '/admin',
};

export const RISK_THRESHOLDS = {
  LOW_MAX: 0.35,     // < 0.35 is Low Risk
  MEDIUM_MAX: 0.60,  // 0.35 to < 0.60 is Medium Risk
  // >= 0.60 is High Risk
};

export const DEPARTMENTS = [
  { code: 'CSD', name: 'Computer Science & Design' },
  { code: 'CSE', name: 'Computer Science & Engineering' },
  { code: 'ISE', name: 'Information Science & Engineering' },
  { code: 'ECE', name: 'Electronics & Communication' },
];

export const SECTIONS = ['A', 'B', 'C'];
export const SEMESTERS = [1, 2, 3, 4, 5, 6, 7, 8];
