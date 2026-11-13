import React, { useState, useEffect } from 'react';
import { Outlet, NavLink, Link, useNavigate, useLocation } from 'react-router-dom';
import {
  GraduationCap,
  ShieldCheck,
  LogOut,
  Moon,
  Sun,
  School,
  Bell,
  HeartHandshake,
  BookOpen,
  User,
  LayoutDashboard,
} from 'lucide-react';
import { ROUTES } from '@/utils/constants';
import { useAuth } from '@/context/AuthContext';
import NotificationCenter from '@/components/notifications/NotificationCenter';
import notificationService from '@/services/notificationService';
import ErrorBoundary from '@/components/common/ErrorBoundary';

const getRoleConfig = (role) => {
  switch (role) {
    case 'student':
      return {
        label: 'Student Portal',
        badgeClass: 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300 border-blue-200 dark:border-blue-800',
        avatarBg: 'bg-blue-600',
        homeRoute: '/student/dashboard',
        allowedRoutes: ['/student/dashboard', '/my-progress'],
        navLinks: [
          { to: '/student/dashboard', label: 'My Academic Dashboard', icon: GraduationCap },
        ],
      };
    case 'parent':
      return {
        label: 'Parent Portal',
        badgeClass: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800',
        avatarBg: 'bg-emerald-600',
        homeRoute: '/parent/dashboard',
        allowedRoutes: ['/parent/dashboard'],
        navLinks: [
          { to: '/parent/dashboard', label: 'Ward Monitoring & Reports', icon: HeartHandshake },
        ],
      };
    case 'teacher':
    case 'hod':
      return {
        label: role === 'hod' ? 'HoD Portal' : 'Faculty Portal',
        badgeClass: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/40 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800',
        avatarBg: 'bg-indigo-600',
        homeRoute: '/teacher/dashboard',
        allowedRoutes: ['/teacher/dashboard'],
        navLinks: [
          { to: '/teacher/dashboard', label: 'Assigned Classes & Marks Entry', icon: BookOpen },
        ],
      };
    case 'principal':
      return {
        label: 'Executive Directorate',
        badgeClass: 'bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300 border-purple-200 dark:border-purple-800',
        avatarBg: 'bg-purple-600',
        homeRoute: '/principal/dashboard',
        allowedRoutes: ['/principal/dashboard'],
        navLinks: [
          { to: '/principal/dashboard', label: 'Institutional Directorate', icon: School },
        ],
      };
    case 'admin':
    default:
      return {
        label: 'System Admin',
        badgeClass: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300 border-amber-200 dark:border-amber-800',
        avatarBg: 'bg-amber-600',
        homeRoute: '/admin/dashboard',
        allowedRoutes: ['/admin/dashboard', '/overview', '/students', '/alerts', '/upload', '/admin'],
        navLinks: [
          { to: '/admin/dashboard', label: 'Admin Directory & Security', icon: ShieldCheck },
          { to: '/principal/dashboard', label: 'Executive Analytics', icon: School },
        ],
      };
  }
};

export default function AppShell() {
  const { currentUser, logout, darkMode, toggleDarkMode } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const [unreadNotifCount, setUnreadNotifCount] = useState(0);

  const roleConfig = getRoleConfig(currentUser?.role || 'student');

  // Enforce strict horizontal route protection:
  // If user tries to access a dashboard not permitted for their role, redirect them to their home route.
  useEffect(() => {
    if (!currentUser) {
      navigate('/login', { replace: true });
      return;
    }
    const currentPath = location.pathname;
    // Allow public or generic routes if needed, otherwise verify allowed routes
    const isAllowed = roleConfig.allowedRoutes.some((route) => currentPath.startsWith(route));
    if (!isAllowed) {
      console.warn(`Role '${currentUser.role}' unauthorized for route '${currentPath}'. Redirecting to ${roleConfig.homeRoute}.`);
      navigate(roleConfig.homeRoute, { replace: true });
    }
  }, [location.pathname, currentUser, navigate, roleConfig]);

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

  const navLinkClass = ({ isActive }) =>
    `inline-flex items-center gap-2 px-3 py-1.5 text-caption font-medium rounded-input transition-colors duration-150 ${
      isActive
        ? 'bg-accent text-white shadow-subtle'
        : 'text-muted hover:text-ink hover:bg-page dark:text-dark-muted dark:hover:text-dark-text dark:hover:bg-dark-surface'
    }`;

  const displayName = currentUser?.name || currentUser?.username || 'Authenticated User';
  const displayUsn = currentUser?.usn ? `(${currentUser.usn})` : '';
  const initials = displayName
    .split(' ')
    .map((w) => w[0])
    .filter(Boolean)
    .slice(0, 2)
    .join('')
    .toUpperCase() || 'U';

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
            <span>Centralized Academic Monitoring (CAMPS-ML)</span>
            <span>&bull;</span>
            <span className="font-mono text-[10px] text-accent-hover">XGBoost + TreeSHAP Active</span>
          </div>
        </div>
      </div>

      {/* Main Navigation Bar */}
      <header className="sticky top-0 z-40 border-b border-line bg-surface/95 px-6 py-2.5 backdrop-blur-md shadow-subtle dark:border-dark-line dark:bg-dark-surface/95">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4">
          {/* Logo & Portal Name */}
          <Link to={roleConfig.homeRoute} className="flex items-center gap-2.5 text-decoration-none">
            <div className="flex h-9 w-9 items-center justify-center rounded-input bg-accent font-heading font-bold text-white shadow-subtle">
              C
            </div>
            <div>
              <span className="font-heading text-heading font-bold tracking-tight text-ink dark:text-dark-text">
                CAMPS-ML
              </span>
              <span className="ml-1.5 hidden rounded-pill bg-accent/10 px-2 py-0.5 text-[10px] font-semibold text-accent sm:inline-block">
                {roleConfig.label}
              </span>
            </div>
          </Link>

          {/* Dynamic Role-Scoped Navigation Menu */}
          <nav className="hidden items-center gap-1.5 md:flex">
            {roleConfig.navLinks.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink key={item.to} to={item.to} className={navLinkClass}>
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>

          {/* User Controls & Authenticated User Profile */}
          <div className="flex items-center gap-3">
            {/* Read-Only Locked User Identity Badge (No Role Switcher Dropdown!) */}
            <div className="flex items-center gap-2 rounded-full border border-line bg-page px-3 py-1 text-caption dark:border-dark-line dark:bg-dark-page">
              <div className={`flex h-6 w-6 items-center justify-center rounded-full text-[10px] font-bold text-white ${roleConfig.avatarBg}`}>
                {initials}
              </div>
              <div className="flex flex-col text-left">
                <span className="text-[11px] font-bold text-ink dark:text-dark-text leading-tight max-w-[130px] sm:max-w-[180px] truncate">
                  {displayName} {displayUsn}
                </span>
                <span className="text-[9px] font-semibold uppercase tracking-wider text-muted dark:text-dark-muted">
                  {roleConfig.label}
                </span>
              </div>
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

            {/* Secure Sign Out Button */}
            <button
              onClick={() => {
                logout();
                navigate('/login');
              }}
              className="flex items-center gap-1 rounded-input border border-line px-2.5 py-1.5 text-caption text-muted transition hover:bg-risk-high/10 hover:text-risk-high dark:border-dark-line dark:text-dark-muted"
              title="Sign out of your session"
            >
              <LogOut className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Sign out</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main App Content */}
      <main className="mx-auto w-full max-w-7xl flex-1 p-4 md:p-6">
        <ErrorBoundary>
          <Outlet />
        </ErrorBoundary>
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
