import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  GraduationCap,
  Users,
  BookOpen,
  ShieldCheck,
  Award,
  ArrowRight,
  School,
  ArrowLeft,
  Lock,
} from 'lucide-react';
import { Card } from '@/components/ui/Card';

const PORTALS = [
  {
    id: 'student',
    title: 'Student Portal',
    roleName: 'Student',
    path: '/login/student',
    icon: GraduationCap,
    badgeColor: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300',
    iconBg: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
    description: 'Access individual subject attendance, CIE test marks, semester results, and study resources.',
    credentialsTip: 'Sign in with your USN (e.g. 4PM23CS071). Default password: password123',
  },
  {
    id: 'parent',
    title: 'Parent Portal',
    roleName: 'Parent / Guardian',
    path: '/login/parent',
    icon: Users,
    badgeColor: 'bg-amber-100 text-amber-800 dark:bg-amber-950/40 dark:text-amber-300',
    iconBg: 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
    description: "Monitor child's academic trajectory, attendance shortage alerts, and communicate with mentors.",
    credentialsTip: 'Sign in with child USN or parent_usn (e.g. parent_4pm23cs071). Password: password123',
  },
  {
    id: 'teacher',
    title: 'Teacher Portal',
    roleName: 'Faculty / Mentor',
    path: '/login/teacher',
    icon: BookOpen,
    badgeColor: 'bg-blue-100 text-blue-800 dark:bg-blue-950/40 dark:text-blue-300',
    iconBg: 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
    description: 'Manage assigned classes, record attendance, enter CIE marks, and dispatch parent notices.',
    credentialsTip: 'Sign in with faculty ID (e.g. anita.rao). Password: password123',
  },
  {
    id: 'admin',
    title: 'Admin Portal',
    roleName: 'System Administrator',
    path: '/login/admin',
    icon: ShieldCheck,
    badgeColor: 'bg-purple-100 text-purple-800 dark:bg-purple-950/40 dark:text-purple-300',
    iconBg: 'bg-purple-500/10 text-purple-600 dark:text-purple-400',
    description: 'Manage user credentials, department structures, class allocations, and audit system events.',
    credentialsTip: 'Sign in with administrator ID (admin). Password: password123',
  },
  {
    id: 'principal',
    title: 'Principal Portal',
    roleName: 'Head of Institution',
    path: '/login/principal',
    icon: Award,
    badgeColor: 'bg-rose-100 text-rose-800 dark:bg-rose-950/40 dark:text-rose-300',
    iconBg: 'bg-rose-500/10 text-rose-600 dark:text-rose-400',
    description: 'Institution-wide academic monitoring, department comparisons, and executive college reports.',
    credentialsTip: 'Sign in with executive ID (principal). Password: password123',
  },
];

export default function ChooseLogin() {
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen flex-col bg-page text-ink dark:bg-dark-page dark:text-dark-text">
      {/* Top Header */}
      <header className="border-b border-line bg-surface/90 px-6 py-4 backdrop-blur-md dark:border-dark-line dark:bg-dark-surface/90">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <Link to="/" className="flex items-center gap-3 text-decoration-none">
            <div className="flex h-10 w-10 items-center justify-center rounded-input bg-accent font-heading text-xl font-bold text-white shadow-subtle">
              P
            </div>
            <div>
              <span className="font-heading text-heading font-bold text-ink dark:text-dark-text">
                PESITM Shivamogga
              </span>
              <p className="text-[11px] text-muted dark:text-dark-muted">
                Smart College Management System &bull; Portal Selection
              </p>
            </div>
          </Link>

          <Link
            to="/"
            className="flex items-center gap-1.5 text-caption font-semibold text-muted hover:text-ink dark:text-dark-muted dark:hover:text-dark-text transition"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Return to College Website</span>
          </Link>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-10 sm:px-6">
        <div className="text-center max-w-2xl mx-auto">
          <span className="inline-flex items-center gap-1.5 rounded-pill bg-accent/10 px-3 py-1 text-caption font-semibold text-accent">
            <Lock className="h-3.5 w-3.5" />
            <span>Role-Based Access Control</span>
          </span>
          <h1 className="mt-3 font-heading text-display font-bold text-ink dark:text-dark-text">
            Choose Your Login Portal
          </h1>
          <p className="mt-2 text-body text-muted dark:text-dark-muted">
            Select your assigned role to access your dedicated dashboard. Credentials are verified against server-side authorization boundaries.
          </p>
        </div>

        {/* 5 Portal Selection Cards */}
        <div className="mt-10 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {PORTALS.map((portal) => {
            const IconComponent = portal.icon;
            return (
              <Card
                key={portal.id}
                onClick={() => navigate(portal.path)}
                className="group relative flex flex-col justify-between transition-all duration-200 hover:-translate-y-1 hover:border-accent hover:shadow-card cursor-pointer"
              >
                <div>
                  <div className="flex items-start justify-between">
                    <div className={`flex h-12 w-12 items-center justify-center rounded-card ${portal.iconBg}`}>
                      <IconComponent className="h-6 w-6" />
                    </div>
                    <span className={`rounded-pill px-2.5 py-0.5 text-[11px] font-semibold ${portal.badgeColor}`}>
                      {portal.roleName}
                    </span>
                  </div>

                  <h3 className="mt-4 font-heading text-heading font-bold text-ink group-hover:text-accent dark:text-dark-text transition">
                    {portal.title}
                  </h3>
                  <p className="mt-1.5 text-caption text-muted dark:text-dark-muted leading-relaxed">
                    {portal.description}
                  </p>
                </div>

                <div className="mt-6 border-t border-line/60 pt-4 dark:border-dark-line/60">
                  <p className="text-[11px] text-muted dark:text-dark-muted italic">
                    {portal.credentialsTip}
                  </p>
                  <div className="mt-3 flex items-center justify-between text-caption font-semibold text-accent">
                    <span>Proceed to Login</span>
                    <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </div>
                </div>
              </Card>
            );
          })}
        </div>

        {/* Security Notice Box */}
        <div className="mt-12 rounded-card border border-line bg-surface p-5 text-caption text-muted dark:border-dark-line dark:bg-dark-surface dark:text-dark-muted text-center max-w-3xl mx-auto">
          <p className="font-semibold text-ink dark:text-dark-text">
            Security Notice &amp; Cross-Portal Prevention
          </p>
          <p className="mt-1">
            Accounts are restricted by strict Role-Based Access Control (RBAC). A student attempting to sign in on the Teacher or Admin portal will be rejected. All sessions are cryptographically signed with short-lived JWTs and audited.
          </p>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-line bg-surface px-6 py-4 text-center text-caption text-muted dark:border-dark-line dark:bg-dark-surface dark:text-dark-muted">
        <p>
          &copy; 2026 PES Institute of Technology &amp; Management, Shivamogga &bull; Smart College Management System
        </p>
      </footer>
    </div>
  );
}
