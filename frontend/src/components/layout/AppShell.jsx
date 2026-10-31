import React from 'react';
import { Outlet, NavLink, Link } from 'react-router-dom';
import { ROUTES } from '@/utils/constants';

export default function AppShell() {
  const navLinkClass = ({ isActive }) =>
    `inline-flex items-center px-3 py-1.5 text-caption font-medium rounded-input transition-colors ${
      isActive
        ? 'bg-accent text-white'
        : 'text-muted hover:text-ink hover:bg-page dark:text-dark-muted dark:hover:text-dark-text dark:hover:bg-dark-surface'
    }`;

  return (
    <div className="flex min-h-screen flex-col bg-page dark:bg-dark-page">
      {/* Top Navbar Skeleton (Full AppShell coming in Phase 3) */}
      <header className="border-b border-line bg-surface px-6 py-3 shadow-subtle dark:border-dark-line dark:bg-dark-surface">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <Link to={ROUTES.OVERVIEW} className="flex items-center gap-2 text-decoration-none">
            <span className="flex h-8 w-8 items-center justify-center rounded-input bg-accent font-heading font-bold text-white">
              C
            </span>
            <span className="font-heading text-heading font-bold text-ink dark:text-dark-text">
              CAMPS-ML
            </span>
          </Link>

          {/* Quick skeleton navigation links for Phase 1 testing */}
          <nav className="flex items-center gap-2">
            <NavLink to={ROUTES.OVERVIEW} className={navLinkClass}>Overview</NavLink>
            <NavLink to={ROUTES.STUDENTS} className={navLinkClass}>Students</NavLink>
            <NavLink to={ROUTES.ALERTS} className={navLinkClass}>Alerts</NavLink>
            <NavLink to={ROUTES.UPLOAD} className={navLinkClass}>Upload</NavLink>
            <NavLink to={ROUTES.MY_PROGRESS} className={navLinkClass}>My Progress</NavLink>
            <NavLink to={ROUTES.ADMIN} className={navLinkClass}>Admin</NavLink>
            <NavLink to={ROUTES.LOGIN} className={navLinkClass}>Sign in</NavLink>
          </nav>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="mx-auto w-full max-w-7xl flex-1 p-6">
        <Outlet />
      </main>
    </div>
  );
}
