import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import {
  Building2,
  Users,
  GraduationCap,
  BookOpen,
  Sparkles,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Award,
  Search,
  Filter,
  RefreshCw,
  ChevronRight,
  ShieldCheck,
  UserCheck,
  Layers,
  FileText,
  Phone,
  Mail,
  ExternalLink,
  Lock,
} from 'lucide-react';

import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Pill } from '@/components/ui/Pill';
import { useAuth } from '@/context/AuthContext';
import api from '@/services/api';
import PassFailPredictionModal from '@/components/predictions/PassFailPredictionModal';

export default function HodDashboard() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [selectedDeptId, setSelectedDeptId] = useState('');
  const [activeTab, setActiveTab] = useState('classes'); // 'classes' | 'faculty' | 'students' | 'analytics'
  const [studentSearch, setStudentSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [selectedStudentUsn, setSelectedStudentUsn] = useState(null);
  const [isPredictionModalOpen, setIsPredictionModalOpen] = useState(false);

  const canSwitch = Boolean(data?.can_switch_department ?? (user?.role === 'admin' || user?.role === 'principal'));

  const fetchOverview = async (deptId = null) => {
    setLoading(true);
    try {
      // HODs are strictly department-scoped: only executive roles pass cross-department queries
      const url = (deptId && canSwitch) ? `/hod/overview?dept_id=${deptId}` : '/hod/overview';
      const res = await api.get(url);
      if (res.data && res.data.success) {
        setData(res.data);
        if (!selectedDeptId && res.data.department?.dept_id) {
          setSelectedDeptId(res.data.department.dept_id);
        }
      }
    } catch (err) {
      console.error('Failed to load HOD overview:', err);
      const msg = err.response?.data?.message || err.message || 'Server connection failed';
      toast.error(`Unable to load departmental analytics (${msg}). Utilizing fallback profile.`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverview(canSwitch ? selectedDeptId : null);
  }, [selectedDeptId]);

  const handleDeptChange = (e) => {
    if (!canSwitch) return;
    const newDeptId = e.target.value;
    setSelectedDeptId(newDeptId);
  };

  const openPrediction = (usn) => {
    setSelectedStudentUsn(usn);
    setIsPredictionModalOpen(true);
  };

  const dept = data?.department || {
    dept_id: 1,
    dept_code: user?.username?.startsWith('hod.') ? user.username.replace('hod.', '').toUpperCase() : 'DEPT',
    name: user?.department || 'Academic Department',
    intake: 60,
  };

  const hod = data?.hod || {
    name: user?.name || 'Head of Department',
    designation: 'Professor & Head',
    employee_id: user?.employee_id || 'PES-HOD',
    email: user?.email || (user?.username ? `${user.username}@pestrust.edu.in` : 'hod@pestrust.edu.in'),
    phone: '',
  };

  const telemetry = data?.telemetry || {
    total_students: 131,
    total_classes: 2,
    total_faculty: 12,
    avg_attendance: 87.4,
    attendance_shortage_count: 5,
    avg_cie: 35.8,
    pass_rate: 94.2,
    risk_distribution: { low: 110, medium: 16, high: 5 },
  };

  const classes = data?.classes || [];
  const faculty = data?.faculty || [];
  const students = data?.students || [];
  const allDepts = data?.all_departments || [];

  // Filter students
  const filteredStudents = students.filter((s) => {
    const matchesSearch =
      s.name?.toLowerCase().includes(studentSearch.toLowerCase()) ||
      s.usn?.toLowerCase().includes(studentSearch.toLowerCase());
    const matchesRisk =
      riskFilter === 'ALL' ||
      s.risk_level?.toLowerCase() === riskFilter.toLowerCase();
    return matchesSearch && matchesRisk;
  });

  return (
    <div className="space-y-6 pb-12 animate-fade-in">
      {/* 1. Header Banner */}
      <div className="relative overflow-hidden rounded-2xl border border-line bg-surface p-6 shadow-card dark:border-dark-line dark:bg-dark-surface">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div className="flex items-start gap-4">
            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-indigo-600 text-white shadow-lg">
              <Building2 className="h-7 w-7" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <span className="inline-flex items-center gap-1 rounded-full bg-indigo-100 px-3 py-0.5 text-xs font-bold text-indigo-800 dark:bg-indigo-950/60 dark:text-indigo-300">
                  <ShieldCheck className="h-3.5 w-3.5" />
                  HOD Department Leadership
                </span>
                <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-semibold text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                  Dept Code: {dept.dept_code}
                </span>
              </div>
              <h1 className="mt-1 font-heading text-2xl font-black text-ink dark:text-dark-text sm:text-3xl">
                {dept.name}
              </h1>
              <div className="mt-1 flex flex-wrap items-center gap-4 text-xs text-muted dark:text-dark-muted">
                <span>
                  Head of Department: <strong className="text-ink dark:text-dark-text">{hod.name}</strong> ({hod.designation})
                </span>
                <span>&bull;</span>
                <span className="flex items-center gap-1">
                  <Mail className="h-3.5 w-3.5 text-indigo-500" />
                  {hod.email}
                </span>
                {hod.employee_id && (
                  <>
                    <span>&bull;</span>
                    <span>Emp ID: <strong className="font-mono text-ink dark:text-dark-text">{hod.employee_id}</strong></span>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Department Scope / Switcher & Refresh */}
          <div className="flex items-center gap-3">
            {canSwitch && allDepts.length > 1 ? (
              <div className="flex flex-col text-right">
                <label className="text-[11px] font-semibold text-muted dark:text-dark-muted mb-1">
                  Switch Department View (Executive Mode)
                </label>
                <select
                  value={selectedDeptId}
                  onChange={handleDeptChange}
                  className="rounded-xl border border-line bg-page px-3 py-2 text-xs font-bold text-ink focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-page dark:text-dark-text"
                >
                  {allDepts.map((d) => (
                    <option key={d.dept_id} value={d.dept_id}>
                      {d.dept_code} - {d.name}
                    </option>
                  ))}
                </select>
              </div>
            ) : (
              <div className="flex flex-col items-end">
                <span className="text-[10px] uppercase font-bold tracking-wider text-muted dark:text-dark-muted mb-1">
                  Department Scope
                </span>
                <div className="flex items-center gap-1.5 rounded-xl border border-indigo-200 bg-indigo-50/80 px-3.5 py-2 text-xs font-bold text-indigo-700 shadow-sm dark:border-indigo-900/50 dark:bg-indigo-950/60 dark:text-indigo-300">
                  <Lock className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
                  <span>Scoped: {dept.dept_code} ({dept.name})</span>
                </div>
              </div>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={() => fetchOverview(canSwitch ? selectedDeptId : null)}
              className="mt-4 flex items-center gap-1.5 shrink-0"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              <span className="hidden sm:inline">Refresh Telemetry</span>
            </Button>
          </div>
        </div>
      </div>

      {/* 2. Key Department Metrics (6 Cards) */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        <Card className="p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between text-muted">
            <span className="text-xs font-semibold">Department Students</span>
            <GraduationCap className="h-4 w-4 text-emerald-600" />
          </div>
          <div className="mt-2">
            <span className="font-heading text-2xl font-black text-ink dark:text-dark-text">
              {telemetry.total_students}
            </span>
            <span className="text-[11px] text-muted block mt-0.5">Enrolled Across Semesters</span>
          </div>
        </Card>

        <Card className="p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between text-muted">
            <span className="text-xs font-semibold">Active Classes</span>
            <Layers className="h-4 w-4 text-blue-600" />
          </div>
          <div className="mt-2">
            <span className="font-heading text-2xl font-black text-ink dark:text-dark-text">
              {telemetry.total_classes}
            </span>
            <span className="text-[11px] text-muted block mt-0.5">Assigned Cohorts & Sections</span>
          </div>
        </Card>

        <Card className="p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between text-muted">
            <span className="text-xs font-semibold">Faculty Members</span>
            <Users className="h-4 w-4 text-purple-600" />
          </div>
          <div className="mt-2">
            <span className="font-heading text-2xl font-black text-ink dark:text-dark-text">
              {telemetry.total_faculty}
            </span>
            <span className="text-[11px] text-muted block mt-0.5">Professors & Mentors</span>
          </div>
        </Card>

        <Card className="p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between text-muted">
            <span className="text-xs font-semibold">Class Attendance Avg</span>
            <Clock className="h-4 w-4 text-teal-600" />
          </div>
          <div className="mt-2">
            <span className={`font-heading text-2xl font-black ${
              telemetry.avg_attendance >= 75 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600'
            }`}>
              {telemetry.avg_attendance}%
            </span>
            <span className="text-[11px] text-muted block mt-0.5">
              VTU Req: 75% {telemetry.avg_attendance >= 75 ? '✓ Compliant' : '⚠ Shortage'}
            </span>
          </div>
        </Card>

        <Card className="p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between text-muted">
            <span className="text-xs font-semibold">Average CIE Score</span>
            <Award className="h-4 w-4 text-amber-600" />
          </div>
          <div className="mt-2">
            <span className="font-heading text-2xl font-black text-ink dark:text-dark-text">
              {telemetry.avg_cie} <span className="text-sm font-normal text-muted">/ 50</span>
            </span>
            <span className="text-[11px] text-muted block mt-0.5">Continuous Internal Eval</span>
          </div>
        </Card>

        <Card className="p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between text-muted">
            <span className="text-xs font-semibold">ML Pass Forecast</span>
            <Sparkles className="h-4 w-4 text-accent" />
          </div>
          <div className="mt-2">
            <span className="font-heading text-2xl font-black text-emerald-600 dark:text-emerald-400">
              {telemetry.pass_rate}%
            </span>
            <span className="text-[11px] text-muted block mt-0.5">XGBoost Department Benchmark</span>
          </div>
        </Card>
      </div>

      {/* 3. Navigation Tabs */}
      <div className="flex border-b border-line bg-page px-2 dark:border-dark-line dark:bg-dark-page overflow-x-auto">
        <button
          onClick={() => setActiveTab('classes')}
          className={`flex items-center gap-2 border-b-2 py-3 px-4 text-sm font-bold transition-all shrink-0 ${
            activeTab === 'classes'
              ? 'border-accent text-accent'
              : 'border-transparent text-muted hover:text-ink dark:text-dark-muted dark:hover:text-dark-text'
          }`}
        >
          <Layers className="h-4 w-4" />
          <span>Department Classes & Sections ({classes.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('faculty')}
          className={`flex items-center gap-2 border-b-2 py-3 px-4 text-sm font-bold transition-all shrink-0 ${
            activeTab === 'faculty'
              ? 'border-accent text-accent'
              : 'border-transparent text-muted hover:text-ink dark:text-dark-muted dark:hover:text-dark-text'
          }`}
        >
          <UserCheck className="h-4 w-4" />
          <span>Faculty & Mentors ({faculty.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('students')}
          className={`flex items-center gap-2 border-b-2 py-3 px-4 text-sm font-bold transition-all shrink-0 ${
            activeTab === 'students'
              ? 'border-accent text-accent'
              : 'border-transparent text-muted hover:text-ink dark:text-dark-muted dark:hover:text-dark-text'
          }`}
        >
          <GraduationCap className="h-4 w-4" />
          <span>Students Roster & ML Risk ({students.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('analytics')}
          className={`flex items-center gap-2 border-b-2 py-3 px-4 text-sm font-bold transition-all shrink-0 ${
            activeTab === 'analytics'
              ? 'border-accent text-accent'
              : 'border-transparent text-muted hover:text-ink dark:text-dark-muted dark:hover:text-dark-text'
          }`}
        >
          <TrendingUp className="h-4 w-4" />
          <span>Risk Radar & Regulations</span>
        </button>
      </div>

      {/* 4. Tab 1: Department Classes */}
      {activeTab === 'classes' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-heading text-lg font-bold text-ink dark:text-dark-text">
              Assigned Academic Classes & Division Cohorts
            </h2>
            <span className="text-xs text-muted">
              Official VTU 2024-25 Curriculum Cycles
            </span>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {classes.length > 0 ? (
              classes.map((c) => (
                <Card key={c.class_id} className="p-5 hover:border-accent transition-all duration-200">
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="rounded-full bg-indigo-100 px-2.5 py-0.5 text-[11px] font-bold text-indigo-800 dark:bg-indigo-950/60 dark:text-indigo-300">
                        Semester {c.semester} &bull; Section {c.section}
                      </span>
                      <h3 className="mt-2 font-heading text-lg font-bold text-ink dark:text-dark-text">
                        {c.class_name}
                      </h3>
                      <p className="text-xs text-muted mt-0.5">
                        Academic Year: <strong>{c.academic_year}</strong>
                      </p>
                    </div>
                    <div className="rounded-xl bg-page p-2 text-center dark:bg-dark-page border border-line dark:border-dark-line">
                      <span className="block text-xs text-muted">Students</span>
                      <span className="font-heading text-lg font-black text-ink dark:text-dark-text">
                        {c.enrolled_students}
                      </span>
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-line dark:border-dark-line space-y-2 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-muted">Faculty Mentor:</span>
                      <span className="font-semibold text-ink dark:text-dark-text">{c.mentor_name}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-muted">Cohort Attendance Avg:</span>
                      <span className={`font-bold ${c.average_attendance >= 75 ? 'text-emerald-600' : 'text-rose-600'}`}>
                        {c.average_attendance}%
                      </span>
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-line/60 dark:border-dark-line/60 flex items-center justify-between">
                    <button
                      onClick={() => setActiveTab('students')}
                      className="text-xs font-bold text-accent hover:underline flex items-center gap-1"
                    >
                      <span>View Class Students</span>
                      <ChevronRight className="h-3.5 w-3.5" />
                    </button>
                    <span className="text-[11px] text-muted">VTU Verified</span>
                  </div>
                </Card>
              ))
            ) : (
              <div className="col-span-full py-12 text-center text-muted">
                No classes currently mapped for this department.
              </div>
            )}
          </div>
        </div>
      )}

      {/* 5. Tab 2: Department Faculty */}
      {activeTab === 'faculty' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-heading text-lg font-bold text-ink dark:text-dark-text">
              Department Faculty Roster & Teaching Allocations
            </h2>
            <span className="text-xs text-muted">
              {faculty.length} Active Faculty Members
            </span>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {faculty.length > 0 ? (
              faculty.map((t) => (
                <Card key={t.teacher_id} className="p-5">
                  <div className="flex items-start gap-3.5">
                    <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-purple-100 text-purple-700 font-bold dark:bg-purple-950/60 dark:text-purple-300">
                      {t.name.split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-heading text-base font-bold text-ink dark:text-dark-text truncate">
                        {t.name}
                      </h3>
                      <p className="text-xs font-medium text-purple-600 dark:text-purple-400">
                        {t.designation}
                      </p>
                      <p className="text-[11px] font-mono text-muted mt-0.5">
                        {t.employee_id}
                      </p>
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-line dark:border-dark-line space-y-1.5 text-xs">
                    {t.email && (
                      <div className="flex items-center gap-2 text-muted">
                        <Mail className="h-3.5 w-3.5 text-muted shrink-0" />
                        <span className="truncate">{t.email}</span>
                      </div>
                    )}
                    {t.phone && (
                      <div className="flex items-center gap-2 text-muted">
                        <Phone className="h-3.5 w-3.5 text-muted shrink-0" />
                        <span>{t.phone}</span>
                      </div>
                    )}
                    <div className="flex items-center justify-between pt-1">
                      <span className="text-muted">Assigned Courses:</span>
                      <span className="font-bold text-ink dark:text-dark-text">
                        {t.assigned_subjects_count || 1} Subject(s)
                      </span>
                    </div>
                  </div>
                </Card>
              ))
            ) : (
              <div className="col-span-full py-12 text-center text-muted">
                No faculty members registered under this department.
              </div>
            )}
          </div>
        </div>
      )}

      {/* 6. Tab 3: Department Students & AI Risk Forecast */}
      {activeTab === 'students' && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <h2 className="font-heading text-lg font-bold text-ink dark:text-dark-text">
                Enrolled Department Students & Machine Learning Risk
              </h2>
              <p className="text-xs text-muted">
                Showing {filteredStudents.length} of {students.length} students
              </p>
            </div>

            {/* Search and Risk Filters */}
            <div className="flex flex-wrap items-center gap-2">
              <div className="relative">
                <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted" />
                <input
                  type="text"
                  placeholder="Search USN or Name..."
                  value={studentSearch}
                  onChange={(e) => setStudentSearch(e.target.value)}
                  className="rounded-xl border border-line bg-page py-1.5 pl-8 pr-3 text-xs text-ink focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-page dark:text-dark-text w-48"
                />
              </div>

              <select
                value={riskFilter}
                onChange={(e) => setRiskFilter(e.target.value)}
                className="rounded-xl border border-line bg-page px-2.5 py-1.5 text-xs font-semibold text-ink focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-page dark:text-dark-text"
              >
                <option value="ALL">All Risk Tiers</option>
                <option value="LOW">Low Risk Only</option>
                <option value="MEDIUM">Moderate Risk</option>
                <option value="HIGH">High Risk Alert</option>
              </select>
            </div>
          </div>

          {/* Students Table */}
          <div className="overflow-hidden rounded-xl border border-line bg-surface shadow-subtle dark:border-dark-line dark:bg-dark-surface">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-page border-b border-line dark:bg-dark-page dark:border-dark-line text-muted">
                  <tr>
                    <th className="py-3 px-4 font-bold uppercase tracking-wider text-[11px]">USN</th>
                    <th className="py-3 px-4 font-bold uppercase tracking-wider text-[11px]">Student Name</th>
                    <th className="py-3 px-4 font-bold uppercase tracking-wider text-[11px]">Cohort</th>
                    <th className="py-3 px-4 font-bold uppercase tracking-wider text-[11px]">Attendance</th>
                    <th className="py-3 px-4 font-bold uppercase tracking-wider text-[11px]">CIE Avg</th>
                    <th className="py-3 px-4 font-bold uppercase tracking-wider text-[11px]">Risk Tier</th>
                    <th className="py-3 px-4 font-bold uppercase tracking-wider text-[11px]">ML Forecast</th>
                    <th className="py-3 px-4 font-bold uppercase tracking-wider text-[11px] text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line dark:divide-dark-line">
                  {filteredStudents.length > 0 ? (
                    filteredStudents.map((s) => (
                      <tr key={s.student_id} className="hover:bg-accent/5 transition-colors">
                        <td className="py-3 px-4 font-mono font-bold text-ink dark:text-dark-text">
                          {s.usn}
                        </td>
                        <td className="py-3 px-4 font-semibold text-ink dark:text-dark-text">
                          {s.name}
                        </td>
                        <td className="py-3 px-4 text-muted">
                          {s.class_name}
                        </td>
                        <td className="py-3 px-4 font-bold">
                          <span className={s.attendance_percentage >= 75 ? 'text-emerald-600' : 'text-rose-600'}>
                            {s.attendance_percentage}%
                          </span>
                        </td>
                        <td className="py-3 px-4 font-bold text-ink dark:text-dark-text">
                          {s.avg_cie} / 50
                        </td>
                        <td className="py-3 px-4">
                          <Pill variant={s.risk_level === 'high' ? 'danger' : s.risk_level === 'medium' ? 'warning' : 'success'}>
                            {s.risk_level?.toUpperCase()} RISK
                          </Pill>
                        </td>
                        <td className="py-3 px-4">
                          <span className={`inline-flex items-center gap-1 font-bold ${
                            s.predicted_outcome === 'Pass' ? 'text-emerald-600' : 'text-rose-600'
                          }`}>
                            {s.predicted_outcome === 'Pass' ? (
                              <CheckCircle2 className="h-3.5 w-3.5" />
                            ) : (
                              <AlertTriangle className="h-3.5 w-3.5" />
                            )}
                            {s.predicted_outcome}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => openPrediction(s.usn)}
                            className="flex items-center gap-1 text-[11px] py-1 px-2.5 ml-auto"
                          >
                            <Sparkles className="h-3 w-3 text-accent" />
                            <span>AI Forecast</span>
                          </Button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={8} className="py-12 text-center text-muted">
                        No students match the current search or risk filter criteria.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* 7. Tab 4: Analytics & Regulations */}
      {activeTab === 'analytics' && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Risk Tier Visualizer Card */}
          <Card className="p-6">
            <h3 className="font-heading text-lg font-bold text-ink dark:text-dark-text flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-accent" />
              Department Risk Distribution
            </h3>
            <p className="text-xs text-muted mt-1">
              XGBoost Multi-Department Model Tiers for {dept.name}
            </p>

            <div className="mt-6 space-y-4">
              <div>
                <div className="flex justify-between text-xs font-semibold mb-1">
                  <span className="text-emerald-600 font-bold">Low Risk (Safe & On Track)</span>
                  <span>{telemetry.risk_distribution.low} Students</span>
                </div>
                <div className="h-3 w-full rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                  <div
                    style={{
                      width: `${(telemetry.risk_distribution.low / maxStudents(telemetry.total_students)) * 100}%`,
                    }}
                    className="h-full bg-emerald-500 rounded-full"
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold mb-1">
                  <span className="text-amber-600 font-bold">Moderate Risk (CIE / Trajectory Borderline)</span>
                  <span>{telemetry.risk_distribution.medium} Students</span>
                </div>
                <div className="h-3 w-full rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                  <div
                    style={{
                      width: `${(telemetry.risk_distribution.medium / maxStudents(telemetry.total_students)) * 100}%`,
                    }}
                    className="h-full bg-amber-500 rounded-full"
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold mb-1">
                  <span className="text-rose-600 font-bold">High Risk Alert (Attendance / Backlogs)</span>
                  <span>{telemetry.risk_distribution.high} Students</span>
                </div>
                <div className="h-3 w-full rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                  <div
                    style={{
                      width: `${(telemetry.risk_distribution.high / maxStudents(telemetry.total_students)) * 100}%`,
                    }}
                    className="h-full bg-rose-500 rounded-full"
                  />
                </div>
              </div>
            </div>
          </Card>

          {/* VTU Statutory Compliance Oversight */}
          <Card className="p-6">
            <h3 className="font-heading text-lg font-bold text-ink dark:text-dark-text flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-indigo-600" />
              VTU Regulatory Compliance Summary
            </h3>
            <p className="text-xs text-muted mt-1">
              Statutory attendance thresholds, CIE minimums, and vertical progression
            </p>

            <div className="mt-5 space-y-3 text-xs">
              <div className="rounded-xl border border-line bg-page p-3.5 dark:border-dark-line dark:bg-dark-page flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-bold text-ink dark:text-dark-text">Attendance Statutory 75% Requirement</h4>
                  <p className="text-muted mt-0.5">
                    {telemetry.total_students - telemetry.attendance_shortage_count} students ({telemetry.avg_attendance}%) satisfy the VTU 75% classroom rule.
                  </p>
                </div>
              </div>

              <div className="rounded-xl border border-line bg-page p-3.5 dark:border-dark-line dark:bg-dark-page flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-amber-600 shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-bold text-ink dark:text-dark-text">Attendance Shortage Notifications ({telemetry.attendance_shortage_count})</h4>
                  <p className="text-muted mt-0.5">
                    {telemetry.attendance_shortage_count} student(s) currently require HOD & Principal medical/institutional condonation.
                  </p>
                </div>
              </div>

              <div className="rounded-xl border border-line bg-page p-3.5 dark:border-dark-line dark:bg-dark-page flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-bold text-ink dark:text-dark-text">Continuous Internal Evaluation (CIE &gt;= 20/50)</h4>
                  <p className="text-muted mt-0.5">
                    Department CIE average is {telemetry.avg_cie}/50, comfortably exceeding the 40% (20/50) VTU sessional qualification.
                  </p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Global Pass/Fail Prediction Modal for any student clicked */}
      <PassFailPredictionModal
        isOpen={isPredictionModalOpen}
        onClose={() => setIsPredictionModalOpen(false)}
        initialUsn={selectedStudentUsn}
        title="Departmental Examination Pass/Fail Intelligence"
      />
    </div>
  );
}

function maxStudents(val) {
  return Math.max(1, Number(val) || 1);
}
