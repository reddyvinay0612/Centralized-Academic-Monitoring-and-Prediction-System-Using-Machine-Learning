import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ROUTES } from '@/utils/constants';

import Landing from '@/pages/Landing';
import ChooseLogin from '@/authentication/ChooseLogin';
import StudentLogin from '@/authentication/StudentLogin';
import ParentLogin from '@/authentication/ParentLogin';
import TeacherLogin from '@/authentication/TeacherLogin';
import AdminLogin from '@/authentication/AdminLogin';
import PrincipalLogin from '@/authentication/PrincipalLogin';
import Login from '@/pages/Login';
import AppShell from '@/components/layout/AppShell';
import Overview from '@/pages/Overview';
import Students from '@/pages/Students';
import StudentProfile from '@/pages/StudentProfile';
import Alerts from '@/pages/Alerts';
import UploadData from '@/pages/UploadData';
import MyProgress from '@/pages/MyProgress';
import Admin from '@/pages/Admin';
import StudentDashboard from '@/dashboards/student/StudentDashboard';
import ParentDashboard from '@/dashboards/parent/ParentDashboard';
import TeacherDashboard from '@/dashboards/teacher/TeacherDashboard';
import AdminDashboard from '@/dashboards/admin/AdminDashboard';
import PrincipalDashboard from '@/dashboards/principal/PrincipalDashboard';
import NotFound from '@/pages/NotFound';

export default function AppRoutes() {
  return (
    <Routes>
      {/* 1. Public College Website Landing Page */}
      <Route path="/" element={<Landing />} />

      {/* 2. Choose Your Login Portal (5 Cards) */}
      <Route path="/login" element={<ChooseLogin />} />

      {/* Role-Specific Login Routes (Dedicated 5 Portal Interfaces) */}
      <Route path="/login/student" element={<StudentLogin />} />
      <Route path="/login/parent" element={<ParentLogin />} />
      <Route path="/login/teacher" element={<TeacherLogin />} />
      <Route path="/login/admin" element={<AdminLogin />} />
      <Route path="/login/principal" element={<PrincipalLogin />} />

      {/* Role-Specific Dedicated Portal Dashboards */}
      <Route path="/student/dashboard" element={<AppShell />}>
        <Route index element={<StudentDashboard />} />
      </Route>
      <Route path="/parent/dashboard" element={<AppShell />}>
        <Route index element={<ParentDashboard />} />
      </Route>
      <Route path="/teacher/dashboard" element={<AppShell />}>
        <Route index element={<TeacherDashboard />} />
      </Route>
      <Route path="/admin/dashboard" element={<AppShell />}>
        <Route index element={<AdminDashboard />} />
      </Route>
      <Route path="/principal/dashboard" element={<AppShell />}>
        <Route index element={<PrincipalDashboard />} />
      </Route>

      {/* 3. Authenticated App Layout & Dashboards */}
      <Route path="/app" element={<AppShell />}>
        <Route index element={<Navigate to={ROUTES.OVERVIEW} replace />} />
        <Route path={ROUTES.OVERVIEW.replace('/', '')} element={<Overview />} />
        <Route path={ROUTES.STUDENTS.replace('/', '')} element={<Students />} />
        <Route path="students/:id" element={<StudentProfile />} />
        <Route path={ROUTES.ALERTS.replace('/', '')} element={<Alerts />} />
        <Route path={ROUTES.UPLOAD.replace('/', '')} element={<UploadData />} />
        <Route path={ROUTES.MY_PROGRESS.replace('/', '')} element={<StudentDashboard />} />
        <Route path="my-progress" element={<StudentDashboard />} />
        <Route path="student/dashboard" element={<StudentDashboard />} />
        <Route path="parent/dashboard" element={<ParentDashboard />} />
        <Route path="teacher/dashboard" element={<TeacherDashboard />} />
        <Route path="admin/dashboard" element={<AdminDashboard />} />
        <Route path="principal/dashboard" element={<PrincipalDashboard />} />
        <Route path={ROUTES.ADMIN.replace('/', '')} element={<AdminDashboard />} />
      </Route>

      {/* Backwards Compatibility Direct Dashboard Routes */}
      <Route path={ROUTES.OVERVIEW} element={<AppShell />}>
        <Route index element={<Overview />} />
      </Route>
      <Route path={ROUTES.STUDENTS} element={<AppShell />}>
        <Route index element={<Students />} />
      </Route>
      <Route path={ROUTES.STUDENT_DETAIL} element={<AppShell />}>
        <Route index element={<StudentProfile />} />
      </Route>
      <Route path={ROUTES.ALERTS} element={<AppShell />}>
        <Route index element={<Alerts />} />
      </Route>
      <Route path={ROUTES.UPLOAD} element={<AppShell />}>
        <Route index element={<UploadData />} />
      </Route>
      <Route path={ROUTES.MY_PROGRESS} element={<AppShell />}>
        <Route index element={<StudentDashboard />} />
      </Route>
      <Route path="/my-progress" element={<AppShell />}>
        <Route index element={<StudentDashboard />} />
      </Route>
      <Route path={ROUTES.ADMIN} element={<AppShell />}>
        <Route index element={<AdminDashboard />} />
      </Route>

      {/* Fallback 404 Route */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
