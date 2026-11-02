/**
 * Application Constants & Role Definitions
 */

export const ROLES = {
  PRINCIPAL: 'principal',
  ADMIN: 'admin',
  HOD: 'hod',
  FACULTY: 'faculty',
  TEACHER: 'teacher',
  PARENT: 'parent',
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
  PRINCIPAL_DASHBOARD: '/principal/dashboard',
  STUDENT_DASHBOARD: '/student/dashboard',
  PARENT_DASHBOARD: '/parent/dashboard',
  TEACHER_DASHBOARD: '/teacher/dashboard',
  ADMIN_DASHBOARD: '/admin/dashboard',
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
