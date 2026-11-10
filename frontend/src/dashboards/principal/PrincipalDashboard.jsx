import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import {
  School,
  Users,
  GraduationCap,
  TrendingUp,
  AlertTriangle,
  FileDown,
  RefreshCw,
  Search,
  Filter,
  Layers,
  Award,
  ChevronRight,
  ShieldCheck,
  CheckCircle2,
  Clock,
  BookOpen,
  UserCheck
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Pill } from '@/components/ui/Pill';
import { DeptComparisonChart } from '@/components/charts/DeptComparisonChart';
import { useAuth } from '@/context/AuthContext';
import principalService from '@/services/principalService';

export default function PrincipalDashboard() {
  const { currentUser } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [downloadingPdf, setDownloadingPdf] = useState(false);

  // Core Data States
  const [overview, setOverview] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [classes, setClasses] = useState([]);
  const [selectedDeptFilter, setSelectedDeptFilter] = useState('all');

  // Students Registry States
  const [students, setStudents] = useState([]);
  const [studentSearch, setStudentSearch] = useState('');
  const [studentRiskFilter, setStudentRiskFilter] = useState('all');
  const [studentDeptFilter, setStudentDeptFilter] = useState('all');
  const [studentsLoading, setStudentsLoading] = useState(false);

  useEffect(() => {
    loadAllPrincipalData();
  }, []);

  const loadAllPrincipalData = async () => {
    setLoading(true);
    try {
      const [overviewData, deptData, classesData] = await Promise.all([
        principalService.getOverview(),
        principalService.getDepartmentMatrix(),
        principalService.getClassCohorts(),
      ]);

      setOverview(overviewData);
      setDepartments(deptData);
      setClasses(classesData);

      // Also load initial students list
      loadStudents();
    } catch (err) {
      console.error('Failed to load Principal Portal data:', err);
      toast.error('Failed to load institutional analytics. Please check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  const loadStudents = async () => {
    setStudentsLoading(true);
    try {
      const params = { limit: 100 };
      if (studentRiskFilter !== 'all') params.risk_level = studentRiskFilter;
      if (studentSearch.trim()) params.search = studentSearch.trim();

      const res = await principalService.getCollegeStudents(params);
      setStudents(res.data || []);
    } catch (err) {
      console.error('Error fetching students:', err);
    } finally {
      setStudentsLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      loadStudents();
    }, 300);
    return () => clearTimeout(timer);
  }, [studentSearch, studentRiskFilter]);

  const handleDownloadReport = async () => {
    setDownloadingPdf(true);
    try {
      toast.loading('Generating Executive Institutional Academic Report (PDF)...', { id: 'pdf-toast' });
      await principalService.downloadExecutiveReport();
      toast.success('Executive Report downloaded successfully.', { id: 'pdf-toast' });
    } catch (err) {
      console.error('PDF download error:', err);
      toast.error('Failed to generate institutional audit PDF.', { id: 'pdf-toast' });
    } finally {
      setDownloadingPdf(false);
    }
  };

  // Filtered Classes based on selected Dept
  const filteredClasses = selectedDeptFilter === 'all'
    ? classes
    : classes.filter(c => c.department_code === selectedDeptFilter);

  // Filtered Students in Registry based on department
  const filteredStudents = studentDeptFilter === 'all'
    ? students
    : students.filter(s => s.department_code === studentDeptFilter);

  if (loading && !overview) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center gap-3">
        <RefreshCw className="h-8 w-8 animate-spin text-accent" />
        <p className="text-body font-medium text-muted">Loading Principal & Executive Analytics...</p>
      </div>
    );
  }

  const { headcount, academic_health, risk_distribution, alerts } = overview || {
    headcount: { total_students: 240, total_faculty: 12, total_departments: 14, total_classes: 12, student_faculty_ratio: 20 },
    academic_health: { college_avg_attendance: 84.5, college_avg_cgpa: 7.92, critical_shortage_records: 18 },
    risk_distribution: { counts: { high: 24, medium: 48, low: 168 }, percentages: { high: 10, medium: 20, low: 70 }, total_evaluated: 240 },
    alerts: { open_alerts: 4, resolved_alerts: 28, total_alerts: 32 }
  };

  return (
    <div className="space-y-6">
      {/* 1. Executive Letterhead & Quick Controls */}
      <div className="relative overflow-hidden rounded-xl border border-line bg-gradient-to-r from-ink via-[#182a4d] to-accent/90 p-6 text-white shadow-elevated dark:border-dark-line">
        <div className="relative z-10 flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-white/10 px-3 py-0.5 text-[11px] font-semibold uppercase tracking-wider text-white backdrop-blur-sm">
                <School className="h-3.5 w-3.5 text-accent-hover" />
                Office of the Principal
              </span>
              <span className="rounded-full bg-emerald-500/20 px-2.5 py-0.5 text-[11px] font-medium text-emerald-300 border border-emerald-500/30">
                VTU Affiliated &bull; PESITM Shivamogga
              </span>
            </div>
            <h1 className="font-heading text-2xl font-bold tracking-tight text-white md:text-3xl">
              Institutional Academic Monitoring & Executive Directorate
            </h1>
            <p className="max-w-2xl text-caption text-white/80">
              Welcome, <span className="font-semibold text-white">{currentUser?.name || 'Dr. Chaitanya Kumar'}</span> (Principal & Director).
              Real-time oversight across {headcount.total_departments || departments.length || 14} academic departments & branches, {headcount.total_students} students, and predictive risk indicators.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={loadAllPrincipalData}
              className="border-white/20 bg-white/10 text-white hover:bg-white/20 backdrop-blur-sm"
              title="Refresh Analytics"
            >
              <RefreshCw className="h-4 w-4" />
              <span className="hidden sm:inline">Refresh</span>
            </Button>
            <Button
              variant="primary"
              size="sm"
              isLoading={downloadingPdf}
              onClick={handleDownloadReport}
              className="bg-accent hover:bg-accent-hover text-white shadow-md border border-accent-hover"
            >
              <FileDown className="h-4 w-4" />
              <span>Download Executive Report (PDF)</span>
            </Button>
          </div>
        </div>
      </div>

      {/* 2. Top-Tier Executive KPI Metrics Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* KPI 1: Student & Faculty Strength */}
        <Card className="border-line bg-surface p-4 shadow-subtle dark:border-dark-line dark:bg-dark-surface">
          <div className="flex items-center justify-between">
            <span className="text-caption font-semibold text-muted dark:text-dark-muted">Total Student Enrollment</span>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/10 text-accent">
              <Users className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-ink dark:text-dark-text">{headcount.total_students}</span>
            <span className="text-[11px] font-medium text-muted dark:text-dark-muted">Students</span>
          </div>
          <div className="mt-2 flex items-center justify-between text-[11px] text-muted dark:text-dark-muted border-t border-line/50 pt-2 dark:border-dark-line/50">
            <span>Faculty: <strong className="text-ink dark:text-dark-text">{headcount.total_faculty}</strong></span>
            <span>Ratio: <strong className="text-accent">{headcount.student_faculty_ratio} : 1</strong></span>
          </div>
        </Card>

        {/* KPI 2: College Attendance Benchmark */}
        <Card className="border-line bg-surface p-4 shadow-subtle dark:border-dark-line dark:bg-dark-surface">
          <div className="flex items-center justify-between">
            <span className="text-caption font-semibold text-muted dark:text-dark-muted">College Attendance Avg</span>
            <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${academic_health.college_avg_attendance >= 75 ? 'bg-emerald-500/10 text-emerald-600' : 'bg-risk-high/10 text-risk-high'}`}>
              <TrendingUp className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-ink dark:text-dark-text">{academic_health.college_avg_attendance}%</span>
            <span className={`text-[11px] font-semibold ${academic_health.college_avg_attendance >= 75 ? 'text-emerald-600 dark:text-emerald-400' : 'text-risk-high'}`}>
              {academic_health.college_avg_attendance >= 75 ? 'VTU Compliant' : 'Shortage Alert'}
            </span>
          </div>
          <div className="mt-2 flex items-center justify-between text-[11px] text-muted dark:text-dark-muted border-t border-line/50 pt-2 dark:border-dark-line/50">
            <span>Critical Shortages (&lt;75%):</span>
            <strong className="text-risk-high">{academic_health.critical_shortage_records} Records</strong>
          </div>
        </Card>

        {/* KPI 3: Cumulative CGPA Benchmark */}
        <Card className="border-line bg-surface p-4 shadow-subtle dark:border-dark-line dark:bg-dark-surface">
          <div className="flex items-center justify-between">
            <span className="text-caption font-semibold text-muted dark:text-dark-muted">Cumulative College CGPA</span>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-500/10 text-purple-600">
              <Award className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-ink dark:text-dark-text">{academic_health.college_avg_cgpa}</span>
            <span className="text-[11px] font-medium text-muted dark:text-dark-muted">/ 10.0 Scale</span>
          </div>
          <div className="mt-2 flex items-center justify-between text-[11px] text-muted dark:text-dark-muted border-t border-line/50 pt-2 dark:border-dark-line/50">
            <span>Engineering Programs:</span>
            <strong className="text-ink dark:text-dark-text">{headcount.total_departments} Branches</strong>
          </div>
        </Card>

        {/* KPI 4: Institutional Risk Distribution */}
        <Card className="border-line bg-surface p-4 shadow-subtle dark:border-dark-line dark:bg-dark-surface">
          <div className="flex items-center justify-between">
            <span className="text-caption font-semibold text-muted dark:text-dark-muted">XGBoost Risk Cohort</span>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500/10 text-amber-600">
              <AlertTriangle className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline gap-1">
            <span className="text-xs font-semibold text-risk-high">{risk_distribution.counts.high} High</span>
            <span className="text-xs text-muted dark:text-dark-muted">&bull;</span>
            <span className="text-xs font-semibold text-amber-500">{risk_distribution.counts.medium} Med</span>
            <span className="text-xs text-muted dark:text-dark-muted">&bull;</span>
            <span className="text-xs font-semibold text-emerald-600">{risk_distribution.counts.low} Low</span>
          </div>
          {/* Proportional Bar */}
          <div className="mt-3 flex h-2 w-full overflow-hidden rounded-full bg-line/50 dark:bg-dark-line">
            <div style={{ width: `${risk_distribution.percentages.high}%` }} className="bg-risk-high" title={`High Risk: ${risk_distribution.counts.high}`} />
            <div style={{ width: `${risk_distribution.percentages.medium}%` }} className="bg-amber-400" title={`Medium Risk: ${risk_distribution.counts.medium}`} />
            <div style={{ width: `${risk_distribution.percentages.low}%` }} className="bg-emerald-500" title={`Low Risk: ${risk_distribution.counts.low}`} />
          </div>
        </Card>
      </div>

      {/* 3. Tab Navigation Bar */}
      <div className="flex border-b border-line dark:border-dark-line">
        <button
          onClick={() => setActiveTab('overview')}
          className={`flex items-center gap-2 border-b-2 px-4 py-3 text-caption font-semibold transition-colors ${
            activeTab === 'overview'
              ? 'border-accent text-accent'
              : 'border-transparent text-muted hover:text-ink dark:text-dark-muted dark:hover:text-dark-text'
          }`}
        >
          <School className="h-4 w-4" />
          <span>Executive Overview & Insights</span>
        </button>

        <button
          onClick={() => setActiveTab('departments')}
          className={`flex items-center gap-2 border-b-2 px-4 py-3 text-caption font-semibold transition-colors ${
            activeTab === 'departments'
              ? 'border-accent text-accent'
              : 'border-transparent text-muted hover:text-ink dark:text-dark-muted dark:hover:text-dark-text'
          }`}
        >
          <Layers className="h-4 w-4" />
          <span>Department Benchmarking Matrix</span>
          <span className="rounded-pill bg-line px-1.5 py-0.2 text-[10px] text-muted dark:bg-dark-line">
            {departments.length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab('classes')}
          className={`flex items-center gap-2 border-b-2 px-4 py-3 text-caption font-semibold transition-colors ${
            activeTab === 'classes'
              ? 'border-accent text-accent'
              : 'border-transparent text-muted hover:text-ink dark:text-dark-muted dark:hover:text-dark-text'
          }`}
        >
          <GraduationCap className="h-4 w-4" />
          <span>Class & Cohort Drilldowns</span>
          <span className="rounded-pill bg-line px-1.5 py-0.2 text-[10px] text-muted dark:bg-dark-line">
            {classes.length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab('students')}
          className={`flex items-center gap-2 border-b-2 px-4 py-3 text-caption font-semibold transition-colors ${
            activeTab === 'students'
              ? 'border-accent text-accent'
              : 'border-transparent text-muted hover:text-ink dark:text-dark-muted dark:hover:text-dark-text'
          }`}
        >
          <Users className="h-4 w-4" />
          <span>College-Wide Student Registry</span>
          <span className="rounded-pill bg-line px-1.5 py-0.2 text-[10px] text-muted dark:bg-dark-line">
            {headcount.total_students}
          </span>
        </button>
      </div>

      {/* 4. Tab 1: Executive Overview & Insights */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            {/* Left 2 Cols: Risk & Academic Intelligence */}
            <div className="space-y-6 lg:col-span-2">
              <Card className="border-line bg-surface p-5 dark:border-dark-line dark:bg-dark-surface">
                <CardHeader className="p-0 pb-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-heading font-bold text-ink dark:text-dark-text">
                        Machine Learning Academic Risk Intelligence (PESITM Model)
                      </CardTitle>
                      <CardDescription className="text-caption text-muted dark:text-dark-muted">
                        Continuous assessment prediction generated by institution-trained XGBoost classification model
                      </CardDescription>
                    </div>
                    <span className="rounded-pill bg-accent/10 px-2.5 py-1 text-xs font-mono font-semibold text-accent">
                      XGBoost + TreeSHAP
                    </span>
                  </div>
                </CardHeader>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                  <div className="rounded-lg border border-risk-high/30 bg-risk-high/5 p-4">
                    <div className="flex items-center justify-between">
                      <span className="text-caption font-semibold text-risk-high">High Academic Risk</span>
                      <span className="rounded-pill bg-risk-high/20 px-2 py-0.5 text-caption font-bold text-risk-high">
                        {risk_distribution.percentages.high}%
                      </span>
                    </div>
                    <p className="mt-2 text-2xl font-bold text-risk-high">{risk_distribution.counts.high}</p>
                    <p className="mt-1 text-[11px] text-muted dark:text-dark-muted">
                      Students requiring immediate mentor counseling & parent communication.
                    </p>
                  </div>

                  <div className="rounded-lg border border-amber-500/30 bg-amber-500/5 p-4">
                    <div className="flex items-center justify-between">
                      <span className="text-caption font-semibold text-amber-600 dark:text-amber-400">Medium Risk</span>
                      <span className="rounded-pill bg-amber-500/20 px-2 py-0.5 text-caption font-bold text-amber-600">
                        {risk_distribution.percentages.medium}%
                      </span>
                    </div>
                    <p className="mt-2 text-2xl font-bold text-amber-600 dark:text-amber-400">{risk_distribution.counts.medium}</p>
                    <p className="mt-1 text-[11px] text-muted dark:text-dark-muted">
                      Borderline CIE performance; recommended for remedial tutorial sessions.
                    </p>
                  </div>

                  <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/5 p-4">
                    <div className="flex items-center justify-between">
                      <span className="text-caption font-semibold text-emerald-600 dark:text-emerald-400">Low Risk (Satisfactory)</span>
                      <span className="rounded-pill bg-emerald-500/20 px-2 py-0.5 text-caption font-bold text-emerald-600">
                        {risk_distribution.percentages.low}%
                      </span>
                    </div>
                    <p className="mt-2 text-2xl font-bold text-emerald-600 dark:text-emerald-400">{risk_distribution.counts.low}</p>
                    <p className="mt-1 text-[11px] text-muted dark:text-dark-muted">
                      Consistent attendance and CIE marks; on-track for university examinations.
                    </p>
                  </div>
                </div>

                <div className="mt-6 rounded-lg border border-line bg-page p-4 dark:border-dark-line dark:bg-dark-page">
                  <h4 className="text-body font-semibold text-ink dark:text-dark-text flex items-center gap-2">
                    <ShieldCheck className="h-4 w-4 text-accent" />
                    Executive Action Directives for Academic Council
                  </h4>
                  <ul className="mt-3 space-y-2 text-caption text-muted dark:text-dark-muted">
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0 mt-0.5" />
                      <span><strong>Directive 1:</strong> All {academic_health.critical_shortage_records} attendance shortage cases must receive formal warning letters before 3rd CIE assessment.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0 mt-0.5" />
                      <span><strong>Directive 2:</strong> HoDs are authorized to organize special Saturday remedial laboratories for subjects with lower class averages.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0 mt-0.5" />
                      <span><strong>Directive 3:</strong> Faculty mentors must complete parent-teacher interactions for all {risk_distribution.counts.high} high-risk students.</span>
                    </li>
                  </ul>
                </div>
              </Card>
            </div>

            {/* Right 1 Col: Institutional Quick Summary */}
            <div className="space-y-6">
              <Card className="border-line bg-surface p-5 dark:border-dark-line dark:bg-dark-surface">
                <CardHeader className="p-0 pb-3">
                  <CardTitle className="text-heading font-bold text-ink dark:text-dark-text">
                    Governance & Audits
                  </CardTitle>
                  <CardDescription className="text-caption text-muted dark:text-dark-muted">
                    Institutional compliance metrics
                  </CardDescription>
                </CardHeader>
                <div className="space-y-3">
                  <div className="flex items-center justify-between rounded-lg border border-line p-3 dark:border-dark-line">
                    <div className="flex items-center gap-2.5">
                      <Clock className="h-4 w-4 text-accent" />
                      <span className="text-caption font-medium text-ink dark:text-dark-text">Open Academic Alerts</span>
                    </div>
                    <span className="font-bold text-amber-500">{alerts.open_alerts}</span>
                  </div>

                  <div className="flex items-center justify-between rounded-lg border border-line p-3 dark:border-dark-line">
                    <div className="flex items-center gap-2.5">
                      <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                      <span className="text-caption font-medium text-ink dark:text-dark-text">Resolved Interventions</span>
                    </div>
                    <span className="font-bold text-emerald-600">{alerts.resolved_alerts}</span>
                  </div>

                  <div className="flex items-center justify-between rounded-lg border border-line p-3 dark:border-dark-line">
                    <div className="flex items-center gap-2.5">
                      <BookOpen className="h-4 w-4 text-purple-500" />
                      <span className="text-caption font-medium text-ink dark:text-dark-text">Accredited Programs</span>
                    </div>
                    <span className="font-bold text-ink dark:text-dark-text">4 NBA/AICTE</span>
                  </div>
                </div>

                <div className="mt-5 border-t border-line pt-4 dark:border-dark-line">
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-center"
                    onClick={handleDownloadReport}
                    isLoading={downloadingPdf}
                  >
                    <FileDown className="h-4 w-4" />
                    <span>Download Audit Summary</span>
                  </Button>
                </div>
              </Card>
            </div>
          </div>

          {/* Institutional Comparative Analytics Recharts Visualizer */}
          <Card className="border-line bg-surface p-5 dark:border-dark-line dark:bg-dark-surface">
            <CardHeader className="p-0 pb-4">
              <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <CardTitle className="text-heading font-bold text-ink dark:text-dark-text">
                    Engineering Programs Comparative Academic Benchmark
                  </CardTitle>
                  <CardDescription className="text-caption text-muted dark:text-dark-muted">
                    Dual-axis comparative distribution of Attendance % (left axis) and Cumulative CGPA (right axis) across engineering branches
                  </CardDescription>
                </div>
                <span className="rounded-pill bg-accent/10 px-2.5 py-1 text-xs font-semibold text-accent">
                  Interactive Dual-Axis Recharts
                </span>
              </div>
            </CardHeader>
            <div className="pt-2">
              <DeptComparisonChart departments={departments} height={300} />
            </div>
          </Card>
        </div>
      )}

      {/* 5. Tab 2: Department Comparative Matrix */}
      {activeTab === 'departments' && (
        <div className="space-y-6">
          <Card className="border-line bg-surface p-5 dark:border-dark-line dark:bg-dark-surface">
            <CardHeader className="p-0 pb-4">
              <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <CardTitle className="text-heading font-bold text-ink dark:text-dark-text">
                    Department Comparative Benchmarking Matrix
                  </CardTitle>
                  <CardDescription className="text-caption text-muted dark:text-dark-muted">
                    Head-to-head performance across all engineering departments for academic governing council review
                  </CardDescription>
                </div>
                <span className="text-caption font-semibold text-muted dark:text-dark-muted">
                  {departments.length || headcount.total_departments || 14} Active Departments
                </span>
              </div>
            </CardHeader>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-line bg-page text-caption font-semibold text-muted dark:border-dark-line dark:bg-dark-page dark:text-dark-muted">
                    <th className="py-3 px-4">Code</th>
                    <th className="py-3 px-4">Department Name</th>
                    <th className="py-3 px-4">Head of Department (HoD)</th>
                    <th className="py-3 px-4 text-center">Students</th>
                    <th className="py-3 px-4 text-center">Faculty</th>
                    <th className="py-3 px-4 text-center">Ratio</th>
                    <th className="py-3 px-4 text-center">Avg Attendance</th>
                    <th className="py-3 px-4 text-center">Avg CGPA</th>
                    <th className="py-3 px-4 text-center">Risk Breakdown</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line text-caption dark:divide-dark-line">
                  {departments.map((dept) => (
                    <tr key={dept.dept_id} className="hover:bg-page/50 transition-colors dark:hover:bg-dark-page/50">
                      <td className="py-3.5 px-4 font-mono font-bold text-accent">
                        {dept.dept_code}
                      </td>
                      <td className="py-3.5 px-4 font-semibold text-ink dark:text-dark-text">
                        {dept.name}
                      </td>
                      <td className="py-3.5 px-4 text-muted dark:text-dark-muted">
                        {dept.hod_name}
                      </td>
                      <td className="py-3.5 px-4 text-center font-bold text-ink dark:text-dark-text">
                        {dept.headcount.students}
                      </td>
                      <td className="py-3.5 px-4 text-center text-muted dark:text-dark-muted">
                        {dept.headcount.faculty}
                      </td>
                      <td className="py-3.5 px-4 text-center font-medium text-accent">
                        {dept.headcount.ratio} : 1
                      </td>
                      <td className="py-3.5 px-4 text-center font-bold">
                        <span className={dept.performance.avg_attendance >= 75 ? 'text-emerald-600 dark:text-emerald-400' : 'text-risk-high'}>
                          {dept.performance.avg_attendance}%
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-center font-bold text-ink dark:text-dark-text">
                        {dept.performance.avg_cgpa}
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <div className="flex items-center justify-center gap-1.5">
                          <span className="rounded-pill bg-risk-high/15 px-2 py-0.5 text-[10px] font-bold text-risk-high">
                            {dept.performance.risk_breakdown.high} H
                          </span>
                          <span className="rounded-pill bg-amber-500/15 px-2 py-0.5 text-[10px] font-bold text-amber-600">
                            {dept.performance.risk_breakdown.medium} M
                          </span>
                          <span className="rounded-pill bg-emerald-500/15 px-2 py-0.5 text-[10px] font-bold text-emerald-600">
                            {dept.performance.risk_breakdown.low} L
                          </span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Visual Benchmarking Distribution */}
          <Card className="border-line bg-surface p-5 dark:border-dark-line dark:bg-dark-surface">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="text-heading font-bold text-ink dark:text-dark-text">
                Department Performance Comparison Graph
              </CardTitle>
              <CardDescription className="text-caption text-muted dark:text-dark-muted">
                Visualizing student attendance compliance alongside cumulative CGPA across engineering departments
              </CardDescription>
            </CardHeader>
            <div className="pt-2">
              <DeptComparisonChart departments={departments} height={280} />
            </div>
          </Card>
        </div>
      )}

      {/* 6. Tab 3: Class & Cohort Drilldowns */}
      {activeTab === 'classes' && (
        <div className="space-y-6">
          <Card className="border-line bg-surface p-5 dark:border-dark-line dark:bg-dark-surface">
            <CardHeader className="p-0 pb-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <CardTitle className="text-heading font-bold text-ink dark:text-dark-text">
                    Class Cohort Academic Inspection
                  </CardTitle>
                  <CardDescription className="text-caption text-muted dark:text-dark-muted">
                    Semester-level breakdown of CIE marks, attendance, and at-risk students
                  </CardDescription>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-caption text-muted dark:text-dark-muted">Filter Dept:</span>
                  <select
                    value={selectedDeptFilter}
                    onChange={(e) => setSelectedDeptFilter(e.target.value)}
                    className="rounded-input border border-line bg-page px-3 py-1.5 text-caption font-medium text-ink focus:outline-none dark:border-dark-line dark:bg-dark-page dark:text-dark-text"
                  >
                    <option value="all">All Departments ({classes.length} Classes)</option>
                    <option value="CSE">Computer Science & Eng (CSE)</option>
                    <option value="ISE">Information Science & Eng (ISE)</option>
                    <option value="ECE">Electronics & Communication (ECE)</option>
                    <option value="CSD">Computer Science & Design (CSD)</option>
                  </select>
                </div>
              </div>
            </CardHeader>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {filteredClasses.map((cls) => (
                <div
                  key={cls.class_id}
                  className="rounded-lg border border-line bg-page p-4 transition-all hover:shadow-subtle dark:border-dark-line dark:bg-dark-page"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="rounded-pill bg-accent/10 px-2 py-0.5 text-[10px] font-bold text-accent">
                        {cls.department_code}
                      </span>
                      <h4 className="mt-1.5 text-body font-bold text-ink dark:text-dark-text">
                        {cls.class_name}
                      </h4>
                      <p className="text-[11px] text-muted dark:text-dark-muted">
                        Semester {cls.semester} &bull; Section {cls.section} &bull; {cls.academic_year}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="text-heading font-bold text-ink dark:text-dark-text">
                        {cls.student_count}
                      </span>
                      <p className="text-[10px] uppercase text-muted dark:text-dark-muted">Students</p>
                    </div>
                  </div>

                  <div className="mt-4 grid grid-cols-3 gap-2 border-t border-line/60 pt-3 text-center dark:border-dark-line/60">
                    <div>
                      <span className="text-[10px] text-muted dark:text-dark-muted">Avg Att.</span>
                      <p className={`text-caption font-bold ${cls.avg_attendance >= 75 ? 'text-emerald-600 dark:text-emerald-400' : 'text-risk-high'}`}>
                        {cls.avg_attendance}%
                      </p>
                    </div>
                    <div>
                      <span className="text-[10px] text-muted dark:text-dark-muted">Avg CIE</span>
                      <p className="text-caption font-bold text-ink dark:text-dark-text">
                        {cls.avg_cie} / 50
                      </p>
                    </div>
                    <div>
                      <span className="text-[10px] text-muted dark:text-dark-muted">At-Risk</span>
                      <p className={`text-caption font-bold ${cls.at_risk_students > 0 ? 'text-risk-high' : 'text-emerald-600'}`}>
                        {cls.at_risk_students}
                      </p>
                    </div>
                  </div>

                  <div className="mt-3 flex items-center justify-between text-[11px] text-muted dark:text-dark-muted">
                    <span>Faculty Mentor:</span>
                    <strong className="text-ink dark:text-dark-text">{cls.mentor_name}</strong>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* 7. Tab 4: College-Wide Student Registry & Risk Directory */}
      {activeTab === 'students' && (
        <div className="space-y-6">
          <Card className="border-line bg-surface p-5 dark:border-dark-line dark:bg-dark-surface">
            <CardHeader className="p-0 pb-4">
              <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <CardTitle className="text-heading font-bold text-ink dark:text-dark-text">
                    College-Wide Student Registry & Predictive Risk Directory
                  </CardTitle>
                  <CardDescription className="text-caption text-muted dark:text-dark-muted">
                    Search and evaluate academic progress and attendance for any student in the institution
                  </CardDescription>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                  {/* Search Input */}
                  <div className="relative min-w-[200px]">
                    <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted" />
                    <input
                      type="text"
                      placeholder="Search USN or Name..."
                      value={studentSearch}
                      onChange={(e) => setStudentSearch(e.target.value)}
                      className="w-full rounded-input border border-line bg-page py-1.5 pl-9 pr-3 text-caption text-ink focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-page dark:text-dark-text"
                    />
                  </div>

                  {/* Dept Filter */}
                  <select
                    value={studentDeptFilter}
                    onChange={(e) => setStudentDeptFilter(e.target.value)}
                    className="rounded-input border border-line bg-page px-3 py-1.5 text-caption font-medium text-ink focus:outline-none dark:border-dark-line dark:bg-dark-page dark:text-dark-text"
                  >
                    <option value="all">All Branches</option>
                    <option value="CSE">CSE</option>
                    <option value="ISE">ISE</option>
                    <option value="ECE">ECE</option>
                    <option value="CSD">CSD</option>
                  </select>

                  {/* Risk Filter */}
                  <select
                    value={studentRiskFilter}
                    onChange={(e) => setStudentRiskFilter(e.target.value)}
                    className="rounded-input border border-line bg-page px-3 py-1.5 text-caption font-medium text-ink focus:outline-none dark:border-dark-line dark:bg-dark-page dark:text-dark-text"
                  >
                    <option value="all">All Risk Levels</option>
                    <option value="high">High Risk Only</option>
                    <option value="medium">Medium Risk</option>
                    <option value="low">Low Risk</option>
                  </select>
                </div>
              </div>
            </CardHeader>

            {studentsLoading ? (
              <div className="flex min-h-[300px] flex-col items-center justify-center gap-2">
                <RefreshCw className="h-6 w-6 animate-spin text-accent" />
                <p className="text-caption text-muted">Querying institutional records...</p>
              </div>
            ) : filteredStudents.length === 0 ? (
              <div className="py-12 text-center text-muted dark:text-dark-muted">
                <p>No student records matching your query criteria.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-line bg-page text-caption font-semibold text-muted dark:border-dark-line dark:bg-dark-page dark:text-dark-muted">
                      <th className="py-3 px-4">USN</th>
                      <th className="py-3 px-4">Student Name</th>
                      <th className="py-3 px-4">Department</th>
                      <th className="py-3 px-4">Class / Section</th>
                      <th className="py-3 px-4 text-center">Attendance %</th>
                      <th className="py-3 px-4 text-center">CGPA</th>
                      <th className="py-3 px-4 text-center">ML Risk Classification</th>
                      <th className="py-3 px-4 text-center">Eligibility Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-line text-caption dark:divide-dark-line">
                    {filteredStudents.map((st) => (
                      <tr key={st.student_id} className="hover:bg-page/50 transition-colors dark:hover:bg-dark-page/50">
                        <td className="py-3 px-4 font-mono font-bold text-accent">
                          {st.usn}
                        </td>
                        <td className="py-3 px-4 font-medium text-ink dark:text-dark-text">
                          {st.name}
                        </td>
                        <td className="py-3 px-4">
                          <span className="rounded-pill bg-accent/10 px-2 py-0.5 text-[10px] font-bold text-accent">
                            {st.department_code}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-muted dark:text-dark-muted">
                          Sem {st.semester} &bull; Sec {st.section}
                        </td>
                        <td className="py-3 px-4 text-center font-bold">
                          <span className={st.attendance_percentage >= 75 ? 'text-emerald-600 dark:text-emerald-400' : 'text-risk-high'}>
                            {st.attendance_percentage}%
                          </span>
                        </td>
                        <td className="py-3 px-4 text-center font-bold text-ink dark:text-dark-text">
                          {st.cgpa}
                        </td>
                        <td className="py-3 px-4 text-center">
                          <Pill level={st.risk_level} variant="risk" />
                        </td>
                        <td className="py-3 px-4 text-center">
                          {st.attendance_percentage >= 75 ? (
                            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">
                              <CheckCircle2 className="h-3 w-3" />
                              VTU Eligible
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-risk-high">
                              <AlertTriangle className="h-3 w-3" />
                              Shortage
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </div>
      )}
    </div>
  );
}
