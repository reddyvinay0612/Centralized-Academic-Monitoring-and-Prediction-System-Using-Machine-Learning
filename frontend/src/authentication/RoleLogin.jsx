import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  GraduationCap,
  Users,
  BookOpen,
  ShieldCheck,
  Award,
  Lock,
  User,
  Eye,
  EyeOff,
  ArrowRight,
  ArrowLeft,
  AlertTriangle,
  Sparkles,
  School,
  CheckCircle2,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { useAuth } from '@/context/AuthContext';
import ForgotPasswordModal from '@/authentication/ForgotPasswordModal';

const ROLE_CONFIGS = {
  student: {
    role: 'student',
    title: 'Student Portal Login',
    subtitle: 'Sign in to access personal marks, subject attendance, timetable, and study resources.',
    icon: GraduationCap,
    badgeText: 'Student Access',
    badgeClass: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300',
    iconBg: 'bg-emerald-500/10 text-emerald-600',
    identifierLabel: 'University Seat Number (USN)',
    identifierPlaceholder: 'e.g. 4PM23CS071 or 4PM22CS001',
    demoCredential: { identifier: '4PM23CS071', password: 'password123', label: 'PAVAN KUMAR (4PM23CS071)' },
    redirectDefault: '/student/dashboard',
  },
  parent: {
    role: 'parent',
    title: 'Parent Portal Login',
    subtitle: "Sign in to monitor your child's academic trajectory, attendance shortage alerts, and teacher remarks.",
    icon: Users,
    badgeText: 'Parent Access',
    badgeClass: 'bg-amber-100 text-amber-800 dark:bg-amber-950/40 dark:text-amber-300',
    iconBg: 'bg-amber-500/10 text-amber-600',
    identifierLabel: 'Registered USN or Parent Username',
    identifierPlaceholder: 'e.g. parent_4pm23cs071 or 4PM23CS071',
    demoCredential: { identifier: 'parent_4pm23cs071', password: 'password123', label: 'Parent of PAVAN KUMAR (4PM23CS071)' },
    redirectDefault: '/parent/dashboard',
  },
  teacher: {
    role: 'teacher',
    title: 'Teacher & Faculty Portal',
    subtitle: 'Sign in to record subject attendance, evaluate CIE marks, and communicate with parents.',
    icon: BookOpen,
    badgeText: 'Faculty Access',
    badgeClass: 'bg-blue-100 text-blue-800 dark:bg-blue-950/40 dark:text-blue-300',
    iconBg: 'bg-blue-500/10 text-blue-600',
    identifierLabel: 'Employee ID or Institutional Email',
    identifierPlaceholder: 'e.g. EMP-CSE-01 or anita.rao@pesitm.edu',
    demoCredential: { identifier: 'EMP-CSE-01', password: 'password123', label: 'Prof. Anita Rao (CSE)' },
    redirectDefault: '/teacher/dashboard',
  },
  admin: {
    role: 'admin',
    title: 'System Administrator Login',
    subtitle: 'Manage user credentials, department structures, class allocations, and audit system events.',
    icon: ShieldCheck,
    badgeText: 'Admin Access',
    badgeClass: 'bg-purple-100 text-purple-800 dark:bg-purple-950/40 dark:text-purple-300',
    iconBg: 'bg-purple-500/10 text-purple-600',
    identifierLabel: 'Administrator Email / Username',
    identifierPlaceholder: 'e.g. admin@pesitm.edu',
    demoCredential: { identifier: 'admin@pesitm.edu', password: 'password123', label: 'Dr. C. G. Halesh (Admin)' },
    redirectDefault: '/admin/dashboard',
  },
  principal: {
    role: 'principal',
    title: 'Principal & Executive Portal',
    subtitle: 'College-wide academic monitoring, department comparisons, and executive audit reports.',
    icon: Award,
    badgeText: 'Executive Access',
    badgeClass: 'bg-rose-100 text-rose-800 dark:bg-rose-950/40 dark:text-rose-300',
    iconBg: 'bg-rose-500/10 text-rose-600',
    identifierLabel: 'Executive Email / Username',
    identifierPlaceholder: 'e.g. principal@pesitm.edu',
    demoCredential: { identifier: 'principal@pesitm.edu', password: 'password123', label: 'Dr. R. S. Hiremath (Principal)' },
    redirectDefault: '/principal/dashboard',
  },
};

export default function RoleLogin({ role = 'student' }) {
  const navigate = useNavigate();
  const { login } = useAuth();
  const config = ROLE_CONFIGS[role] || ROLE_CONFIGS.student;
  const RoleIcon = config.icon;

  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [isForgotModalOpen, setIsForgotModalOpen] = useState(false);

  // Fill sample demo credentials for examiners/graders
  const handleQuickFill = () => {
    setIdentifier(config.demoCredential.identifier);
    setPassword(config.demoCredential.password);
    setErrorMessage('');
    toast.success(`Populated sample credentials for ${config.demoCredential.label}`);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');

    if (!identifier.trim() || !password) {
      setErrorMessage('Please provide both your identifier and password.');
      return;
    }

    setIsLoading(true);
    const result = await login(identifier.trim(), password, config.role);
    setIsLoading(false);

    if (result.success) {
      toast.success(`Welcome to the ${config.title}!`);
      // Navigate to dedicated role dashboard
      navigate(result.redirectTo || config.redirectDefault);
    } else {
      setErrorMessage(result.message || 'Invalid credentials.');
      toast.error(result.message || 'Authentication failed.');
    }
  };

  return (
    <div className="flex min-h-screen flex-col bg-page text-ink dark:bg-dark-page dark:text-dark-text">
      {/* Top Header */}
      <header className="border-b border-line bg-surface/90 px-6 py-3.5 backdrop-blur-md dark:border-dark-line dark:bg-dark-surface/90">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5 text-decoration-none">
            <div className="flex h-9 w-9 items-center justify-center rounded-input bg-accent font-heading text-lg font-bold text-white shadow-subtle">
              P
            </div>
            <div>
              <span className="font-heading text-body font-bold text-ink dark:text-dark-text">
                PESITM Shivamogga
              </span>
              <p className="text-[10px] text-muted dark:text-dark-muted">
                Smart College Management System
              </p>
            </div>
          </Link>

          <Link
            to="/login"
            className="flex items-center gap-1.5 text-caption font-semibold text-muted hover:text-ink dark:text-dark-muted dark:hover:text-dark-text transition"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            <span>Change Portal</span>
          </Link>
        </div>
      </header>

      {/* Main Login Card Form */}
      <main className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center px-4 py-12">
        <div className="rounded-card border border-line bg-surface p-6 sm:p-8 shadow-card dark:border-dark-line dark:bg-dark-surface">
          {/* Header & Role Badge */}
          <div className="flex items-start justify-between">
            <div className={`flex h-12 w-12 items-center justify-center rounded-card ${config.iconBg}`}>
              <RoleIcon className="h-6 w-6" />
            </div>
            <span className={`rounded-pill px-2.5 py-0.5 text-[11px] font-semibold ${config.badgeClass}`}>
              {config.badgeText}
            </span>
          </div>

          <h1 className="mt-4 font-heading text-display font-bold text-ink dark:text-dark-text">
            {config.title}
          </h1>
          <p className="mt-1 text-caption text-muted dark:text-dark-muted leading-relaxed">
            {config.subtitle}
          </p>

          {/* Error & Lockout Message Alert */}
          {errorMessage && (
            <div className="mt-4 flex items-start gap-2.5 rounded-input border border-risk-high/30 bg-risk-high/10 p-3 text-caption text-risk-high">
              <AlertTriangle className="h-4 w-4 flex-shrink-0 mt-0.5" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="mt-5 space-y-4">
            <div>
              <label className="mb-1 block text-caption font-medium text-ink dark:text-dark-text">
                {config.identifierLabel} <span className="text-risk-high">*</span>
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
                <input
                  type="text"
                  required
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  placeholder={config.identifierPlaceholder}
                  className="w-full rounded-input border border-line bg-surface py-2 pl-9 pr-3 text-body text-ink transition focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                />
              </div>
            </div>

            <div>
              <div className="mb-1 flex items-center justify-between">
                <label className="text-caption font-medium text-ink dark:text-dark-text">
                  Password <span className="text-risk-high">*</span>
                </label>
                <button
                  type="button"
                  onClick={() => setIsForgotModalOpen(true)}
                  className="text-[11px] font-semibold text-accent hover:underline"
                >
                  Forgot password?
                </button>
              </div>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full rounded-input border border-line bg-surface py-2 pl-9 pr-10 text-body text-ink transition focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-ink focus:outline-none"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              <p className="mt-1.5 text-[11px] text-muted dark:text-dark-muted flex items-center justify-between">
                <span>Default password for all accounts:</span>
                <span className="font-mono font-semibold text-accent bg-accent/10 px-1.5 py-0.5 rounded">password123</span>
              </p>
            </div>

            <Button
              type="submit"
              variant="primary"
              className="w-full mt-2"
              isLoading={isLoading}
            >
              <span>Sign In to {config.badgeText}</span>
              <ArrowRight className="h-4 w-4" />
            </Button>
          </form>

          {/* Quick 1-Click Demo Fill for Viva Examiner */}
          <div className="mt-6 border-t border-line/60 pt-4 dark:border-dark-line/60">
            <button
              type="button"
              onClick={handleQuickFill}
              className="flex w-full items-center justify-center gap-2 rounded-input border border-dashed border-accent/40 bg-accent/5 p-2 text-caption font-medium text-accent hover:bg-accent/10 transition"
            >
              <Sparkles className="h-3.5 w-3.5" />
              <span>Fill Demo Credentials ({config.demoCredential.label})</span>
            </button>
          </div>
        </div>

        {/* Back Link */}
        <div className="mt-6 text-center text-caption text-muted">
          <span>Wrong portal? </span>
          <Link to="/login" className="font-semibold text-accent hover:underline">
            Choose a different user login
          </Link>
        </div>
      </main>

      {/* Forgot Password Modal */}
      <ForgotPasswordModal
        isOpen={isForgotModalOpen}
        onClose={() => setIsForgotModalOpen(false)}
      />

      {/* Institutional Footer */}
      <footer className="border-t border-line bg-surface px-6 py-4 text-center text-[11px] text-muted dark:border-dark-line dark:bg-dark-surface dark:text-dark-muted">
        PES Institute of Technology &amp; Management &bull; Department of Computer Science &amp; Engineering &bull; VTU Affiliated
      </footer>
    </div>
  );
}
