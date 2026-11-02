import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  School,
  Lock,
  User,
  ShieldCheck,
  GraduationCap,
  Users,
  Eye,
  EyeOff,
  ArrowRight,
  Sparkles,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useAuth } from '@/context/AuthContext';
import { INITIAL_USERS } from '@/mocks/data';
import { ROUTES } from '@/utils/constants';

export default function Login() {
  const navigate = useNavigate();
  const { loginAsUser } = useAuth();

  const [identifier, setIdentifier] = useState('admin@pesitm.edu');
  const [password, setPassword] = useState('admin123');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);

    setTimeout(() => {
      setIsLoading(false);
      // Find matching user or fallback to admin
      const matched =
        INITIAL_USERS.find(
          (u) =>
            u.email.toLowerCase() === identifier.toLowerCase() ||
            u.username.toLowerCase() === identifier.toLowerCase() ||
            u.usn?.toLowerCase() === identifier.toLowerCase()
        ) || INITIAL_USERS[0];

      loginAsUser(matched);
      toast.success(`Welcome back, ${matched.name}!`);

      if (matched.role === 'student' || matched.role === 'parent') {
        navigate(ROUTES.MY_PROGRESS);
      } else if (matched.role === 'admin') {
        navigate(ROUTES.ADMIN);
      } else {
        navigate(ROUTES.OVERVIEW);
      }
    }, 450);
  };

  const handleQuickLogin = (user) => {
    loginAsUser(user);
    toast.success(`Authenticated as ${user.name} (${user.role.toUpperCase()})`);
    if (user.role === 'student' || user.role === 'parent') {
      navigate(ROUTES.MY_PROGRESS);
    } else if (user.role === 'admin') {
      navigate(ROUTES.ADMIN);
    } else {
      navigate(ROUTES.OVERVIEW);
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-page p-4 dark:bg-dark-page">
      {/* Institution Header */}
      <div className="mb-6 text-center">
        <div className="inline-flex h-12 w-12 items-center justify-center rounded-card bg-accent font-heading text-2xl font-bold text-white shadow-card">
          C
        </div>
        <h1 className="mt-3 font-heading text-display font-bold text-ink dark:text-dark-text">
          CAMPS-ML Portal
        </h1>
        <p className="text-body text-muted dark:text-dark-muted">
          PES Institute of Technology & Management &bull; VTU Belagavi
        </p>
      </div>

      {/* Main Login Card */}
      <div className="w-full max-w-md rounded-card border border-line bg-surface p-6 sm:p-8 shadow-card dark:border-dark-line dark:bg-dark-surface">
        <h2 className="font-heading text-heading font-semibold text-ink dark:text-dark-text">
          Institutional Sign In
        </h2>
        <p className="mt-1 text-caption text-muted dark:text-dark-muted">
          Sign in with your PESITM institutional email or USN.
        </p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label className="mb-1.5 block text-caption font-medium text-ink dark:text-dark-text">
              Email Address / USN
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
              <input
                type="text"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder="e.g. admin@pesitm.edu or 4PM21CS000"
                className="w-full rounded-input border border-line bg-surface py-2 pl-9 pr-3 text-body text-ink transition focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                required
              />
            </div>
          </div>

          <div>
            <label className="mb-1.5 block text-caption font-medium text-ink dark:text-dark-text">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full rounded-input border border-line bg-surface py-2 pl-9 pr-10 text-body text-ink transition focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-ink"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          <Button
            type="submit"
            variant="primary"
            className="w-full"
            isLoading={isLoading}
          >
            <span>Sign In to Dashboard</span>
            <ArrowRight className="h-4 w-4" />
          </Button>
        </form>

        {/* 1-Click Quick Login Demo Section */}
        <div className="mt-6 border-t border-line/60 pt-5 dark:border-dark-line/60">
          <div className="flex items-center gap-1.5 text-caption font-semibold text-muted dark:text-dark-muted">
            <Sparkles className="h-3.5 w-3.5 text-accent" />
            <span>Viva & Demo Quick Switch (1-Click Login):</span>
          </div>

          <div className="mt-3 grid grid-cols-2 gap-2">
            <button
              onClick={() => handleQuickLogin(INITIAL_USERS[0])}
              className="flex items-center gap-2 rounded-input border border-line bg-page/50 p-2 text-left text-caption transition hover:border-accent hover:bg-surface dark:border-dark-line dark:bg-dark-page"
            >
              <ShieldCheck className="h-4 w-4 text-purple-600 flex-shrink-0" />
              <div>
                <p className="font-semibold text-ink dark:text-dark-text leading-tight">Admin</p>
                <p className="text-[10px] text-muted">Dr. Halesh</p>
              </div>
            </button>

            <button
              onClick={() => handleQuickLogin(INITIAL_USERS[1])}
              className="flex items-center gap-2 rounded-input border border-line bg-page/50 p-2 text-left text-caption transition hover:border-accent hover:bg-surface dark:border-dark-line dark:bg-dark-page"
            >
              <Users className="h-4 w-4 text-blue-600 flex-shrink-0" />
              <div>
                <p className="font-semibold text-ink dark:text-dark-text leading-tight">Teacher</p>
                <p className="text-[10px] text-muted">Prof. Anita Rao</p>
              </div>
            </button>

            <button
              onClick={() => handleQuickLogin(INITIAL_USERS[4])}
              className="flex items-center gap-2 rounded-input border border-line bg-page/50 p-2 text-left text-caption transition hover:border-accent hover:bg-surface dark:border-dark-line dark:bg-dark-page"
            >
              <GraduationCap className="h-4 w-4 text-emerald-600 flex-shrink-0" />
              <div>
                <p className="font-semibold text-ink dark:text-dark-text leading-tight">Student</p>
                <p className="text-[10px] text-muted">Poorvi V S</p>
              </div>
            </button>

            <button
              onClick={() => handleQuickLogin(INITIAL_USERS[6])}
              className="flex items-center gap-2 rounded-input border border-line bg-page/50 p-2 text-left text-caption transition hover:border-accent hover:bg-surface dark:border-dark-line dark:bg-dark-page"
            >
              <User className="h-4 w-4 text-amber-600 flex-shrink-0" />
              <div>
                <p className="font-semibold text-ink dark:text-dark-text leading-tight">Parent</p>
                <p className="text-[10px] text-muted">Smt. Shailaja V</p>
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <p className="mt-6 text-center text-caption text-muted dark:text-dark-muted">
        Department of Computer Science & Engineering &bull; PESITM Shivamogga
      </p>
    </div>
  );
}
