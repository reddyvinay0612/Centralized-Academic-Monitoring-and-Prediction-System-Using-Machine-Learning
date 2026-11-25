import React from 'react';
import {
  X,
  Building2,
  Users,
  BookOpen,
  Award,
  Mail,
  Phone,
  MapPin,
  CheckCircle2,
  Cpu,
  Layers,
  ArrowRight,
  ShieldCheck,
  GraduationCap
} from 'lucide-react';
import { Button } from '@/components/ui/Button';

export default function DepartmentDetailsModal({ isOpen, onClose, department }) {
  if (!isOpen || !department) return null;

  const faculty = department.faculty || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-y-auto animate-fade-in">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-950/70 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Modal Dialog */}
      <div className="relative w-full max-w-4xl rounded-2xl bg-surface border border-line shadow-2xl overflow-hidden z-10 dark:bg-dark-surface dark:border-dark-line my-8 max-h-[90vh] flex flex-col">
        {/* Modal Top Header with Photo Banner */}
        <div className="relative h-48 sm:h-56 w-full overflow-hidden shrink-0 bg-slate-900">
          <img
            src={department.imageUrl}
            alt={department.name}
            className="h-full w-full object-cover opacity-60"
            onError={(e) => {
              e.target.src = 'https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=1200&q=80';
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/60 to-transparent" />

          {/* Close Button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 h-9 w-9 rounded-full bg-black/50 hover:bg-black/80 text-white flex items-center justify-center transition focus:outline-none backdrop-blur-md"
            aria-label="Close modal"
          >
            <X className="h-5 w-5" />
          </button>

          {/* Banner Content */}
          <div className="absolute bottom-4 left-6 right-6 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
            <div>
              <div className="flex flex-wrap items-center gap-2 mb-1.5">
                <span className="rounded-md bg-blue-600 px-2.5 py-0.5 text-xs font-bold text-white uppercase tracking-wider">
                  {department.code}
                </span>
                <span className="rounded-md bg-white/20 backdrop-blur-md px-2.5 py-0.5 text-xs font-semibold text-white">
                  {department.categoryLabel || 'Academic Program'}
                </span>
                <span className="rounded-md bg-emerald-500/80 backdrop-blur-md px-2.5 py-0.5 text-xs font-semibold text-white">
                  Intake: {department.intake}
                </span>
              </div>
              <h2 className="font-heading text-2xl sm:text-3xl font-extrabold text-white leading-tight">
                {department.name}
              </h2>
            </div>
          </div>
        </div>

        {/* Modal Body: Scrollable Content */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* 1. Department Overview */}
          <div>
            <h3 className="font-heading text-base font-bold text-ink dark:text-dark-text flex items-center gap-2">
              <Building2 className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              <span>Department Overview &amp; Curriculum Scope</span>
            </h3>
            <p className="mt-2 text-sm text-muted dark:text-dark-muted leading-relaxed">
              {department.description}
            </p>
          </div>

          {/* 2. Head of Department Profile Card */}
          <div className="rounded-xl border border-indigo-200/80 bg-gradient-to-br from-indigo-50/70 via-white to-indigo-50/30 p-5 dark:border-indigo-900/50 dark:from-indigo-950/40 dark:via-dark-surface dark:to-indigo-950/20">
            <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-700 dark:text-indigo-400">
              Department Leadership
            </span>
            <div className="mt-3 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className="h-14 w-14 rounded-full bg-indigo-600 text-white font-heading font-black text-xl flex items-center justify-center shrink-0 shadow-md">
                  {department.head ? department.head.split(' ').map(n => n[0]).filter(Boolean).slice(-2).join('') : 'HD'}
                </div>
                <div>
                  <h4 className="font-heading text-lg font-bold text-ink dark:text-dark-text">
                    {department.head}
                  </h4>
                  <p className="text-xs font-semibold text-indigo-600 dark:text-indigo-400">
                    {department.designation || 'Professor & Head'}
                  </p>
                  <p className="text-[11px] text-muted dark:text-dark-muted mt-0.5">
                    Department of {department.name} &bull; PESITM Shivamogga
                  </p>
                </div>
              </div>

              {/* HOD Contact Meta */}
              <div className="flex flex-col gap-1.5 text-xs text-muted dark:text-dark-muted sm:text-right">
                {department.email && (
                  <a
                    href={`mailto:${department.email}`}
                    className="flex items-center sm:justify-end gap-1.5 font-mono text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    <Mail className="h-3.5 w-3.5" />
                    <span>{department.email}</span>
                  </a>
                )}
                <span className="flex items-center sm:justify-end gap-1.5">
                  <Phone className="h-3.5 w-3.5 text-slate-400" />
                  <span>+91 94482 10000 &bull; Office Ext: 204</span>
                </span>
                <span className="flex items-center sm:justify-end gap-1.5 text-[11px]">
                  <MapPin className="h-3.5 w-3.5 text-slate-400" />
                  <span>Academic Block, 2nd Floor, PESITM Campus</span>
                </span>
              </div>
            </div>
          </div>

          {/* 3. Faculty & Mentors Directory */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-heading text-base font-bold text-ink dark:text-dark-text flex items-center gap-2">
                <Users className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                <span>Department Faculty &amp; Research Mentors ({faculty.length + 1})</span>
              </h3>
              <span className="text-xs font-medium text-muted dark:text-dark-muted">
                Official VTU &amp; PESITM Accredited Faculty
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              {/* HOD Card in Faculty list */}
              <div className="rounded-lg border border-indigo-200 bg-indigo-50/40 p-3.5 dark:border-indigo-900/40 dark:bg-indigo-950/20">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-indigo-600 text-white font-bold text-sm flex items-center justify-center shrink-0">
                    {department.head ? department.head.split(' ').map(n => n[0]).filter(Boolean).slice(-2).join('') : 'HD'}
                  </div>
                  <div className="min-w-0">
                    <p className="font-heading text-xs font-bold text-ink dark:text-dark-text truncate">
                      {department.head}
                    </p>
                    <p className="text-[11px] font-semibold text-indigo-700 dark:text-indigo-300 truncate">
                      {department.designation || 'Professor & Head'}
                    </p>
                    <p className="text-[10px] text-muted dark:text-dark-muted truncate mt-0.5">
                      {department.email}
                    </p>
                  </div>
                </div>
              </div>

              {/* Department Teachers */}
              {faculty.map((f, idx) => (
                <div
                  key={f.teacher_id || idx}
                  className="rounded-lg border border-line bg-surface p-3.5 shadow-subtle hover:border-accent transition dark:border-dark-line dark:bg-dark-surface"
                >
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200 font-bold text-sm flex items-center justify-center shrink-0 border border-slate-200 dark:border-slate-700">
                      {f.name.split(' ').map(n => n[0]).filter(Boolean).slice(-2).join('')}
                    </div>
                    <div className="min-w-0">
                      <p className="font-heading text-xs font-bold text-ink dark:text-dark-text truncate">
                        {f.name}
                      </p>
                      <p className="text-[11px] text-muted dark:text-dark-muted truncate">
                        {f.designation}
                      </p>
                      <p className="text-[10px] text-blue-600 dark:text-blue-400 truncate mt-0.5 font-mono">
                        {f.email || `${f.name.toLowerCase().replace(/[^a-z]/g, '.')}@pestrust.edu.in`}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 4. Specialized Laboratories & Research Centers */}
          {department.labs && (
            <div className="rounded-xl border border-line bg-page/50 p-4 dark:border-dark-line dark:bg-dark-page/40">
              <h3 className="font-heading text-xs font-bold text-ink dark:text-dark-text uppercase tracking-wider flex items-center gap-1.5">
                <Cpu className="h-4 w-4 text-purple-600" />
                <span>Specialized Laboratories &amp; Research Centers</span>
              </h3>
              <div className="mt-2.5 flex flex-wrap gap-2">
                {department.labs.split(',').map((lab, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center gap-1 rounded-md bg-surface px-2.5 py-1 text-xs font-medium text-slate-700 shadow-subtle border border-line dark:bg-dark-surface dark:border-dark-line dark:text-slate-300"
                  >
                    <CheckCircle2 className="h-3 w-3 text-emerald-500" />
                    <span>{lab.trim()}</span>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="border-t border-line bg-page/80 px-6 py-4 flex flex-col sm:flex-row items-center justify-between gap-3 shrink-0 dark:border-dark-line dark:bg-dark-page/80">
          <div className="text-xs text-muted dark:text-dark-muted">
            PESITM Autonomous System &bull; Affiliated to Visvesvaraya Technological University (VTU)
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm" onClick={onClose}>
              Close Window
            </Button>
            <a
              href="/login/hod"
              className="inline-flex items-center justify-center gap-1.5 rounded-input bg-indigo-600 px-4 py-2 text-xs font-bold text-white shadow hover:bg-indigo-700 transition"
            >
              <ShieldCheck className="h-4 w-4" />
              <span>HOD Portal Login</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
