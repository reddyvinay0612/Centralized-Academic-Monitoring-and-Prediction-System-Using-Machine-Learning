import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ROUTES } from '@/utils/constants';

import AppShell from '@/components/layout/AppShell';
import Login from '@/pages/Login';
import Overview from '@/pages/Overview';
import Students from '@/pages/Students';
import StudentProfile from '@/pages/StudentProfile';
import Alerts from '@/pages/Alerts';
import UploadData from '@/pages/UploadData';
import MyProgress from '@/pages/MyProgress';
import Admin from '@/pages/Admin';
import NotFound from '@/pages/NotFound';

export default function AppRoutes() {
  return (
    <Routes>
      {/* Public Authentication Route */}
      <Route path={ROUTES.LOGIN} element={<Login />} />

      {/* Main Authenticated Layout Shell */}
      <Route path="/" element={<AppShell />}>
        {/* Default route redirect to Overview */}
        <Route index element={<Navigate to={ROUTES.OVERVIEW} replace />} />

        {/* Core Application Pages */}
        <Route path={ROUTES.OVERVIEW} element={<Overview />} />
        <Route path={ROUTES.STUDENTS} element={<Students />} />
        <Route path={ROUTES.STUDENT_DETAIL} element={<StudentProfile />} />
        <Route path={ROUTES.ALERTS} element={<Alerts />} />
        <Route path={ROUTES.UPLOAD} element={<UploadData />} />
        <Route path={ROUTES.MY_PROGRESS} element={<MyProgress />} />
        <Route path={ROUTES.ADMIN} element={<Admin />} />
      </Route>

      {/* Fallback 404 Route */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
