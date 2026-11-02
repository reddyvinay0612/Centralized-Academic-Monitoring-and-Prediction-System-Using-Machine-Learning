import React, { useState, useEffect } from 'react';
import { Outlet, NavLink, Link, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  AlertTriangle,
  UploadCloud,
  GraduationCap,
  ShieldCheck,
  LogOut,
  Moon,
  Sun,
  School,
  ChevronDown,
  Bell,
} from 'lucide-react';
import { ROUTES } from '@/utils/constants';
import { useAuth } from '@/context/AuthContext';
import { INITIAL_USERS } from '@/mocks/data';
import NotificationCenter from '@/components/notifications/NotificationCenter';
import notificationService from '@/services/notificationService';

export default function AppShell() {
  const { currentUser, switchRole, logout, darkMode, toggleDarkMode } = useAuth();
  const navigate = useNavigate();
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const [unreadNotifCount, setUnreadNotifCount] = useState(0);

  useEffect(() => {
    let isMounted = true;
    const fetchUnread = async () => {
      try {
        const count = await notificationService.getUnreadCount();
        if (isMounted) setUnreadNotifCount(count || 0);
      } catch (e) {
        // Fallback silently if offline or token expired
      }
    };
    fetchUnread();
    const interval = setInterval(fetchUnread, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [currentUser]);

  const handleRoleChange = (e) => {
    const role = e.target.value;
    switchRole(role);
    if (role === 'student') {
      navigate('/student/dashboard');
    } else if (role === 'parent') {
      navigate('/parent/dashboard');
    } else if (role === 'teacher') {
      navigate('/teacher/dashboard');
    } else if (role === 'principal') {
      navigate('/principal/dashboard');
    } else if (role === 'admin') {
      navigate('/admin/dashboard');
    } else {
      navigate(ROUTES.OVERVIEW);
    }
  };

  const navLinkClass = ({ isActive }) =>
    `inline-flex items-center gap-2 px-3 py-1.5 text-caption font-medium rounded-input transition-colors duration-150 ${
      isActive
        ? 'bg-accent text-white shadow-subtle'
        : 'text-muted hover:text-ink hover:bg-page dark:text-dark-muted dark:hover:text-dark-text dark:hover:bg-dark-surface'
    }`;

  return (
    <div className="flex min-h-screen flex-col bg-page text-ink dark:bg-dark-page dark:text-dark-text">
      {/* Top Academic Institution Banner */}
      <div className="border-b border-line/60 bg-ink px-6 py-1.5 text-[11px] font-medium text-white/90 dark:border-dark-line">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div className="flex items-center gap-2">
            <School className="h-3.5 w-3.5 text-accent-hover" />
            <span>PES Institute of Technology and Management, Shivamogga &bull; VTU Affiliated</span>
          </div>
          <div className="flex items-center gap-3 text-white/70">
            <span>Dept. of Computer Science & Engineering</span>
            <span>&bull;</span>
            <span className="font-mono text-[10px] text-accent-hover">XGBoost v1.0.0 Active</span>
          </div>
        </div>
      </div>

      {/* Main Navigation Bar */}
      <header className="sticky top-0 z-40 border-b border-line bg-surface/95 px-6 py-2.5 backdrop-blur-md shadow-subtle dark:border-dark-line dark:bg-dark-surface/95">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4">
          {/* Logo & Platform Name */}
          <Link to={ROUTES.OVERVIEW} className="flex items-center gap-2.5 text-decoration-none">
            <div className="flex h-9 w-9 items-center justify-center rounded-input bg-accent font-heading font-bold text-white shadow-subtle">
              C
            </div>
            <div>
              <span className="font-heading text-heading font-bold tracking-tight text-ink dark:text-dark-text">
                CAMPS-ML
              </span>
              <span className="ml-1.5 hidden rounded-pill bg-accent/10 px-2 py-0.5 text-[10px] font-semibold text-accent sm:inline-block">
                Academic Monitor
              </span>
            </div>
          </Link>

          {/* Navigation Menu */}
          <nav className="hidden items-center gap-1.5 md:flex">
            <NavLink to={ROUTES.OVERVIEW} className={navLinkClass}>
              <LayoutDashboard className="h-4 w-4" />
              <span>Overview</span>
            </NavLink>
            <NavLink to={ROUTES.STUDENTS} className={navLinkClass}>
              <Users className="h-4 w-4" />
              <span>Students</span>
            </NavLink>
            <NavLink to={ROUTES.ALERTS} className={navLinkClass}>
              <div className="relative">
                <AlertTriangle className="h-4 w-4" />
                <span className="absolute -top-1 -right-1 flex h-2 w-2 rounded-full bg-risk-high" />
              </div>
              <span>Alerts</span>
            </NavLink>
            <NavLink to={ROUTES.UPLOAD} className={navLinkClass}>
              <UploadCloud className="h-4 w-4" />
              <span>Upload</span>
            </NavLink>
            <NavLink to={ROUTES.MY_PROGRESS} className={navLinkClass}>
              <GraduationCap className="h-4 w-4" />
              <span>My Progress</span>
            </NavLink>
            <NavLink to={ROUTES.ADMIN} className={navLinkClass}>
              <ShieldCheck className="h-4 w-4" />
              <span>Admin</span>
            </NavLink>
            <NavLink to="/principal/dashboard" className={navLinkClass}>
              <School className="h-4 w-4" />
              <span>Principal</span>
            </NavLink>
          </nav>

          {/* User Controls & Role Quick Switcher */}
          <div className="flex items-center gap-2.5">
            {/* Quick Persona / Role Switcher for viva demo */}
            <div className="flex items-center gap-1.5 rounded-input border border-line bg-page px-2.5 py-1 text-caption dark:border-dark-line dark:bg-dark-page">
              <span className="text-[11px] font-semibold uppercase text-muted dark:text-dark-muted hidden sm:inline">
                Role:
              </span>
              <select
                value={currentUser?.role || 'admin'}
                onChange={handleRoleChange}
                className="bg-transparent text-caption font-semibold text-ink dark:text-dark-text focus:outline-none cursor-pointer"
                title="Switch role for demo inspection"
              >
                <option value="principal">Principal (Dr. Chaitanya)</option>
                <option value="admin">Admin (Dr. Halesh)</option>
                <option value="teacher">Teacher (Prof. Rao)</option>
                <option value="student">Student (Poorvi)</option>
                <option value="parent">Parent (Smt. Shailaja)</option>
              </select>
            </div>

            {/* Notification Bell Button */}
            <button
              onClick={() => setIsNotifOpen(true)}
              className="relative rounded-input border border-line p-2 text-muted transition hover:bg-page hover:text-ink dark:border-dark-line dark:text-dark-muted dark:hover:bg-dark-page dark:hover:text-dark-text"
              aria-label="View notifications"
              title="Official notices & notifications"
            >
              <Bell className="h-4 w-4" />
              {unreadNotifCount > 0 && (
                <span className="absolute -top-1 -right-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-accent px-1 text-[10px] font-bold text-white shadow-xs">
                  {unreadNotifCount > 9 ? '9+' : unreadNotifCount}
                </span>
              )}
            </button>

            {/* Dark Mode Toggle */}
            <button
              onClick={toggleDarkMode}
              className="rounded-input border border-line p-2 text-muted transition hover:bg-page hover:text-ink dark:border-dark-line dark:text-dark-muted dark:hover:bg-dark-page dark:hover:text-dark-text"
              aria-label="Toggle dark mode"
              title="Toggle theme"
            >
              {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>

            {/* Sign Out */}
            <button
              onClick={() => {
                logout();
                navigate(ROUTES.LOGIN);
              }}
              className="flex items-center gap-1 rounded-input border border-line px-2.5 py-1.5 text-caption text-muted transition hover:bg-risk-high/10 hover:text-risk-high dark:border-dark-line dark:text-dark-muted"
              title="Sign out"
            >
              <LogOut className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Sign out</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main App Content */}
      <main className="mx-auto w-full max-w-7xl flex-1 p-4 md:p-6">
        <Outlet />
      </main>

      {/* Institution Footer */}
      <footer className="mt-auto border-t border-line bg-surface px-6 py-4 text-center text-caption text-muted dark:border-dark-line dark:bg-dark-surface dark:text-dark-muted">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-2 sm:flex-row">
          <span>
            &copy; 2024-2025 PESITM Shivamogga &bull; Department of Computer Science & Engineering
          </span>
          <span className="font-mono text-[11px]">
            Final-Year Capstone Project &bull; XGBoost + TreeSHAP + VTU Analytics
          </span>
        </div>
      </footer>
      {/* In-Portal Notification Center Drawer */}
      <NotificationCenter
        isOpen={isNotifOpen}
        onClose={() => setIsNotifOpen(false)}
        onUnreadCountChange={setUnreadNotifCount}
      />
    </div>
  );
}
