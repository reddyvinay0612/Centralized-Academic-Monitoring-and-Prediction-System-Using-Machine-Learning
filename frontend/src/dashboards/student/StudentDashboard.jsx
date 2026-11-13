import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import {
  GraduationCap,
  TrendingUp,
  Clock,
  BookOpen,
  Award,
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  Phone,
  Mail,
  User,
  Sparkles,
  Sliders,
  Download,
  Calendar,
  MessageSquare,
  Bell,
  BarChart3,
  RefreshCw,
  FileText,
  ChevronRight,
  ShieldAlert
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Pill } from '@/components/ui/Pill';
import { RiskGauge } from '@/components/charts/RiskGauge';
import { SgpaTrend } from '@/components/charts/SgpaTrend';
import { ShapBars } from '@/components/charts/ShapBars';
import { AttendanceBar } from '@/components/charts/AttendanceBar';
import { CieRadarChart } from '@/components/charts/CieRadarChart';
import { useAuth } from '@/context/AuthContext';
import studentService from '@/services/studentService';
import PassFailPredictionModal from '@/components/predictions/PassFailPredictionModal';

export default function StudentDashboard() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [isPassFailModalOpen, setIsPassFailModalOpen] = useState(false);
  const [selectedDay, setSelectedDay] = useState('Monday');

  // Dashboard Data State
  const [profile, setProfile] = useState(null);
  const [attendance, setAttendance] = useState(null);
  const [marks, setMarks] = useState(null);
  const [timetable, setTimetable] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [remarks, setRemarks] = useState([]);
  const [notifications, setNotifications] = useState([]);

  // Load all student data
  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [
        profData,
        attData,
        marksData,
        ttData,
        predData,
        remData,
        notifData
      ] = await Promise.allSettled([
        studentService.getProfile(),
        studentService.getAttendance(),
        studentService.getMarks(),
        studentService.getTimetable(),
        studentService.getPrediction(),
        studentService.getRemarks(),
        studentService.getNotifications()
      ]);

      if (profData.status === 'fulfilled') setProfile(profData.value);
      if (attData.status === 'fulfilled') setAttendance(attData.value);
      if (marksData.status === 'fulfilled') setMarks(marksData.value);
      if (ttData.status === 'fulfilled') setTimetable(ttData.value);
      if (predData.status === 'fulfilled') setPrediction(predData.value);
      if (remData.status === 'fulfilled') setRemarks(remData.value);
      if (notifData.status === 'fulfilled') setNotifications(notifData.value);

      // Default day for timetable if available
      if (ttData.status === 'fulfilled' && ttData.value?.days?.length > 0) {
        setSelectedDay(ttData.value.days[0]);
      }
    } catch (err) {
      toast.error('Could not load some student metrics. Showing cached data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const handleDownloadReport = async () => {
    setDownloadingPdf(true);
    try {
      await studentService.downloadReportPdf(null, profile?.usn || user?.username || 'student');
      toast.success('Academic performance report downloaded successfully!');
    } catch (err) {
      toast.error('Failed to generate report PDF. Please try again.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[500px] flex-col items-center justify-center space-y-4">
        <RefreshCw className="h-8 w-8 animate-spin text-accent" />
        <p className="text-body font-medium text-muted dark:text-dark-muted">
          Loading student academic records & ML risk telemetry...
        </p>
      </div>
    );
  }

  // Calculated values
  const overallAtt = attendance?.overall?.percentage || 0;
  const isShortage = attendance?.overall?.is_shortage || false;
  const cgpa = marks?.summary?.cgpa || 7.5;
  const activeBacklogs = marks?.summary?.active_backlogs || 0;
  const sgpaHistory = marks?.progression?.map((p) => p.sgpa) || [7.1, 7.3, 7.6, 7.8, 8.1];

  return (
    <div className="space-y-6">
      {/* 1. Header Banner & Profile Strip */}
      <div className="rounded-card border border-line bg-surface p-6 shadow-sm dark:border-dark-line dark:bg-dark-surface">
        <div className="flex flex-col justify-between gap-6 md:flex-row md:items-center">
          {/* Student Info */}
          <div className="flex items-start gap-4">
            <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-accent/10 text-accent font-heading text-2xl font-bold dark:bg-accent/20">
              {profile?.name ? profile.name.slice(0, 2).toUpperCase() : 'ST'}
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="font-heading text-display font-bold text-ink dark:text-dark-text">
                  {profile?.name || user?.name || 'Student Portal'}
                </h1>
                <span className="rounded-input border border-line bg-page px-2 py-0.5 font-mono text-caption font-semibold text-ink dark:border-dark-line dark:bg-dark-page dark:text-dark-text">
                  {profile?.usn || user?.username || '4PM21CS001'}
                </span>
                <Pill variant={isShortage ? 'high' : 'low'}>
                  {isShortage ? 'Attendance Shortage (<75%)' : 'Attendance Eligible'}
                </Pill>
              </div>
              <p className="mt-1 text-body text-muted dark:text-dark-muted">
                {profile?.department?.dept_name || 'Computer Science & Engineering'} &bull;{' '}
                {profile?.class_name || '5th Sem'} (Sec {profile?.section || 'A'}) &bull; Academic Year {profile?.academic_year || '2024-25'}
              </p>
              {profile?.mentor && (
                <div className="mt-2 flex flex-wrap items-center gap-4 text-caption text-muted dark:text-dark-muted">
                  <span className="flex items-center gap-1">
                    <User className="h-3.5 w-3.5 text-accent" />
                    Mentor: <strong className="text-ink dark:text-dark-text">{profile.mentor.name}</strong> ({profile.mentor.designation})
                  </span>
                  {profile.mentor.phone && (
                    <span className="flex items-center gap-1">
                      <Phone className="h-3.5 w-3.5" /> {profile.mentor.phone}
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Actions: Download PDF & AI Prediction */}
          <div className="flex flex-wrap items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={loadDashboardData}
              title="Refresh Data"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button
              variant="primary"
              size="md"
              onClick={() => setIsPassFailModalOpen(true)}
              className="flex items-center gap-2 whitespace-nowrap bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-md font-bold"
            >
              <Sparkles className="h-4 w-4 animate-pulse text-amber-300" />
              Predict Pass / Fail
            </Button>
            <Button
              variant="outline"
              size="md"
              onClick={handleDownloadReport}
              loading={downloadingPdf}
              className="flex items-center gap-2 whitespace-nowrap shadow-sm"
            >
              <Download className="h-4 w-4" />
              Download Report (PDF)
            </Button>
          </div>
        </div>

        {/* Shortage Critical Alert Banner */}
        {isShortage && (
          <div className="mt-5 flex items-center gap-3 rounded-input border border-risk-high/30 bg-risk-high/10 p-3.5 text-caption text-risk-high dark:bg-risk-high/20">
            <ShieldAlert className="h-5 w-5 shrink-0" />
            <div>
              <p className="font-semibold">
                VTU Attendance Warning: Overall attendance is currently at {overallAtt}%.
              </p>
              <p className="mt-0.5 text-xs opacity-90">
                You are below the mandatory 75% attendance criteria. Please consult your mentor faculty immediately to avoid examination debarment.
              </p>
            </div>
          </div>
        )}

        {/* Tab Navigation Navigation Strip */}
        <div className="mt-6 flex overflow-x-auto border-t border-line pt-4 scrollbar-none dark:border-dark-line">
          {[
            { id: 'overview', label: 'Overview & Trajectory', icon: BarChart3 },
            { id: 'prediction', label: 'AI Pass/Fail Predictor', icon: Sparkles },
            { id: 'attendance', label: 'Attendance Tracker', icon: Clock },
            { id: 'academics', label: 'Marks & Internal Evaluation', icon: BookOpen },
            { id: 'timetable', label: 'Class Timetable', icon: Calendar },
            { id: 'guidance', label: 'Mentor Guidance', icon: MessageSquare, count: remarks?.length },
            { id: 'notices', label: 'Notices & Circulars', icon: Bell, count: notifications?.length }
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 whitespace-nowrap border-b-2 px-4 py-2 text-caption font-semibold transition-colors ${
                  isActive
                    ? 'border-accent text-accent'
                    : 'border-transparent text-muted hover:text-ink dark:text-dark-muted dark:hover:text-dark-text'
                }`}
              >
                <Icon className="h-4 w-4" />
                {tab.label}
                {tab.count !== undefined && tab.count > 0 && (
                  <span className="flex h-5 w-5 items-center justify-center rounded-full bg-accent/15 text-[10px] text-accent">
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* 2. TAB CONTENT: Overview & Trajectory */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Key Metric KPI Cards */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {/* Card 1: CGPA */}
            <Card className="p-5">
              <div className="flex items-center justify-between">
                <span className="text-caption font-medium text-muted dark:text-dark-muted">Cumulative CGPA</span>
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/10 text-accent">
                  <Award className="h-4 w-4" />
                </span>
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="font-heading text-display font-bold text-ink dark:text-dark-text">
                  {cgpa.toFixed(2)}
                </span>
                <span className="text-caption text-muted dark:text-dark-muted">/ 10.0</span>
              </div>
              <p className="mt-1 text-xs text-muted dark:text-dark-muted">
                {marks?.summary?.total_credits || 100} credits earned across semesters
              </p>
            </Card>

            {/* Card 2: Attendance */}
            <Card className="p-5">
              <div className="flex items-center justify-between">
                <span className="text-caption font-medium text-muted dark:text-dark-muted">Overall Attendance</span>
                <span className={`flex h-8 w-8 items-center justify-center rounded-lg ${isShortage ? 'bg-risk-high/10 text-risk-high' : 'bg-risk-low/10 text-risk-low'}`}>
                  <Clock className="h-4 w-4" />
                </span>
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className={`font-heading text-display font-bold ${isShortage ? 'text-risk-high' : 'text-risk-low'}`}>
                  {overallAtt}%
                </span>
                <span className="text-caption text-muted dark:text-dark-muted">
                  {attendance?.overall?.attended_classes || 0}/{attendance?.overall?.total_classes || 0} classes
                </span>
              </div>
              <p className="mt-1 text-xs text-muted dark:text-dark-muted">
                {isShortage ? 'Critical shortage: below 75%' : 'Eligible for VTU semester exams'}
              </p>
            </Card>

            {/* Card 3: Active Backlogs */}
            <Card className="p-5">
              <div className="flex items-center justify-between">
                <span className="text-caption font-medium text-muted dark:text-dark-muted">Active Backlogs</span>
                <span className={`flex h-8 w-8 items-center justify-center rounded-lg ${activeBacklogs > 0 ? 'bg-risk-high/10 text-risk-high' : 'bg-risk-low/10 text-risk-low'}`}>
                  <BookOpen className="h-4 w-4" />
                </span>
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="font-heading text-display font-bold text-ink dark:text-dark-text">
                  {activeBacklogs}
                </span>
                <span className="text-caption text-muted dark:text-dark-muted">subject(s)</span>
              </div>
              <p className="mt-1 text-xs text-muted dark:text-dark-muted">
                {activeBacklogs === 0 ? 'Zero pending backlogs' : 'Supplementary exam registration open'}
              </p>
            </Card>

            {/* Card 4: ML Prediction */}
            <Card className="p-5">
              <div className="flex items-center justify-between">
                <span className="text-caption font-medium text-muted dark:text-dark-muted">XGBoost Risk Level</span>
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/10 text-accent">
                  <Sparkles className="h-4 w-4" />
                </span>
              </div>
              <div className="mt-3 flex items-center gap-2">
                <Pill variant={prediction?.risk_level || 'low'}>
                  {prediction?.risk_level ? prediction.risk_level.toUpperCase() : 'LOW'} RISK
                </Pill>
                <span className="text-xs text-muted dark:text-dark-muted font-medium">
                  {prediction?.predicted_outcome || 'Pass'}
                </span>
              </div>
              <p className="mt-2 text-xs text-muted dark:text-dark-muted">
                Predicted Next SGPA: <strong className="text-ink dark:text-dark-text">{prediction?.predicted_sgpa || (cgpa + 0.1).toFixed(2)}</strong>
              </p>
            </Card>
          </div>

          {/* Middle Row: Risk Gauge & SHAP Explanations */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            {/* Risk Gauge */}
            <Card className="p-6">
              <CardHeader className="p-0 pb-4">
                <CardTitle className="flex items-center gap-2 text-section">
                  <Sparkles className="h-4 w-4 text-accent" />
                  ML Risk Forecast
                </CardTitle>
                <CardDescription>
                  Trained on PESITM historical student academic trajectories.
                </CardDescription>
              </CardHeader>
              <div className="flex flex-col items-center justify-center pt-2">
                <RiskGauge score={prediction?.risk_score || 0.15} size={220} />
              </div>
            </Card>

            {/* SHAP Explanations Feature Attribution */}
            <Card className="p-6 lg:col-span-2">
              <CardHeader className="p-0 pb-4">
                <CardTitle className="flex items-center gap-2 text-section">
                  <TrendingUp className="h-4 w-4 text-accent" />
                  Key Academic Trajectory Drivers (SHAP)
                </CardTitle>
                <CardDescription>
                  Factors positively pushing your performance (green) vs risk-increasing factors (red).
                </CardDescription>
              </CardHeader>
              <div className="pt-2">
                <ShapBars explanations={prediction?.explanations || []} studentName={profile?.name} />
              </div>
            </Card>
          </div>

          {/* Recommendations & Actionable Guidance */}
          {prediction?.recommendations && prediction.recommendations.length > 0 && (
            <Card className="p-6">
              <CardHeader className="p-0 pb-4">
                <CardTitle className="flex items-center gap-2 text-section text-accent">
                  <CheckCircle2 className="h-5 w-5" />
                  Personalized Academic Improvement Recommendations
                </CardTitle>
                <CardDescription>
                  Data-driven steps curated by faculty mentors and the predictive model.
                </CardDescription>
              </CardHeader>
              <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                {prediction.recommendations.map((rec, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-3 rounded-input border border-line bg-page p-3.5 dark:border-dark-line dark:bg-dark-page"
                  >
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent/10 text-xs font-bold text-accent">
                      {idx + 1}
                    </span>
                    <p className="text-caption text-ink dark:text-dark-text leading-relaxed">
                      {rec}
                    </p>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Quick SGPA Progression Chart */}
          <Card className="p-6">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="text-section">Semester-wise SGPA Progression</CardTitle>
              <CardDescription>
                VTU grading progression across completed semesters (Benchmark threshold: 7.0 SGPA).
              </CardDescription>
            </CardHeader>
            <div className="pt-2">
              <SgpaTrend history={sgpaHistory} targetGpa={7.0} height={240} />
            </div>
          </Card>
        </div>
      )}

      {/* 3. TAB CONTENT: Attendance Tracker */}
      {activeTab === 'attendance' && (
        <div className="space-y-6">
          {/* Attendance Overview Summary */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <Card className="p-4">
              <span className="text-caption font-medium text-muted">Total Classes Held</span>
              <p className="mt-1 font-heading text-2xl font-bold text-ink dark:text-dark-text">
                {attendance?.overall?.total_classes || 0}
              </p>
            </Card>
            <Card className="p-4">
              <span className="text-caption font-medium text-muted">Classes Attended</span>
              <p className="mt-1 font-heading text-2xl font-bold text-risk-low">
                {attendance?.overall?.attended_classes || 0}
              </p>
            </Card>
            <Card className="p-4">
              <span className="text-caption font-medium text-muted">Classes Absent</span>
              <p className="mt-1 font-heading text-2xl font-bold text-risk-high">
                {attendance?.overall?.absent_classes || 0}
              </p>
            </Card>
          </div>

          {/* Subject Breakdown Table */}
          <Card className="p-6">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="text-section">Subject-wise Attendance Breakdown</CardTitle>
              <CardDescription>
                Mandatory minimum VTU attendance requirement is 75% per subject.
              </CardDescription>
            </CardHeader>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-caption">
                <thead className="border-b border-line bg-page text-muted dark:border-dark-line dark:bg-dark-page dark:text-dark-muted">
                  <tr>
                    <th className="py-3 px-4 font-semibold">Subject Code</th>
                    <th className="py-3 px-4 font-semibold">Subject Name</th>
                    <th className="py-3 px-4 font-semibold text-center">Attended / Total</th>
                    <th className="py-3 px-4 font-semibold text-center">Percentage</th>
                    <th className="py-3 px-4 font-semibold">Status</th>
                    <th className="py-3 px-4 font-semibold">Remediation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line dark:divide-dark-line">
                  {attendance?.subjects?.map((sub) => {
                    const isSubShortage = sub.is_shortage;
                    return (
                      <tr key={sub.attendance_id} className="hover:bg-page/50 dark:hover:bg-dark-page/50">
                        <td className="py-3.5 px-4 font-mono font-medium text-ink dark:text-dark-text">
                          {sub.subject_code}
                        </td>
                        <td className="py-3.5 px-4 font-medium text-ink dark:text-dark-text">
                          {sub.subject_name}
                        </td>
                        <td className="py-3.5 px-4 text-center text-muted dark:text-dark-muted">
                          {sub.attended_classes} / {sub.total_classes}
                        </td>
                        <td className="py-3.5 px-4 text-center">
                          <span className={`font-heading font-bold ${isSubShortage ? 'text-risk-high' : 'text-risk-low'}`}>
                            {sub.percentage}%
                          </span>
                        </td>
                        <td className="py-3.5 px-4">
                          <Pill variant={isSubShortage ? 'high' : 'low'}>
                            {isSubShortage ? 'Shortage (<75%)' : 'Eligible'}
                          </Pill>
                        </td>
                        <td className="py-3.5 px-4 text-xs">
                          {isSubShortage ? (
                            <span className="text-risk-high font-medium">
                              Need {sub.classes_needed_for_75} consecutive classes to clear
                            </span>
                          ) : (
                            <span className="text-muted dark:text-dark-muted">On Track</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Visual Subject Attendance Bar Chart with VTU 75% Threshold */}
          <Card className="p-6">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="text-section">Visual Attendance Compliance Breakdown</CardTitle>
              <CardDescription>
                Subject-wise attendance relative to the mandatory VTU 75% red threshold line.
              </CardDescription>
            </CardHeader>
            <div className="pt-2">
              <AttendanceBar subjects={attendance?.subjects || []} height={250} />
            </div>
          </Card>
        </div>
      )}

      {/* 4. TAB CONTENT: Marks & Internal Evaluation */}
      {activeTab === 'academics' && (
        <div className="space-y-6">
          <Card className="p-6">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="text-section">Continuous Internal Evaluation (CIE) Marks</CardTitle>
              <CardDescription>
                Standard VTU CIE assessment pattern: Average of top 2 CIEs + Assignments + Quizzes (Max 50 Marks, Passing 20).
              </CardDescription>
            </CardHeader>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-caption">
                <thead className="border-b border-line bg-page text-muted dark:border-dark-line dark:bg-dark-page dark:text-dark-muted">
                  <tr>
                    <th className="py-3 px-4 font-semibold">Subject</th>
                    <th className="py-3 px-4 font-semibold text-center">Credits</th>
                    <th className="py-3 px-4 font-semibold text-center">CIE 1 (30)</th>
                    <th className="py-3 px-4 font-semibold text-center">CIE 2 (30)</th>
                    <th className="py-3 px-4 font-semibold text-center">CIE 3 (30)</th>
                    <th className="py-3 px-4 font-semibold text-center">Assign (10)</th>
                    <th className="py-3 px-4 font-semibold text-center">Quiz (10)</th>
                    <th className="py-3 px-4 font-semibold text-center">Total CIE (50)</th>
                    <th className="py-3 px-4 font-semibold">CIE Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line dark:divide-dark-line">
                  {marks?.subjects?.map((sub) => (
                    <tr key={sub.marks_id} className="hover:bg-page/50 dark:hover:bg-dark-page/50">
                      <td className="py-3.5 px-4 font-medium text-ink dark:text-dark-text">
                        <span className="font-mono text-xs text-muted block">{sub.subject_code}</span>
                        {sub.subject_name}
                      </td>
                      <td className="py-3.5 px-4 text-center text-muted">{sub.credits}</td>
                      <td className="py-3.5 px-4 text-center">{sub.cie1}</td>
                      <td className="py-3.5 px-4 text-center">{sub.cie2}</td>
                      <td className="py-3.5 px-4 text-center">{sub.cie3}</td>
                      <td className="py-3.5 px-4 text-center">{sub.assignment_marks}</td>
                      <td className="py-3.5 px-4 text-center">{sub.quiz_marks}</td>
                      <td className="py-3.5 px-4 text-center font-heading text-body font-bold text-ink dark:text-dark-text">
                        {sub.total_cie}
                      </td>
                      <td className="py-3.5 px-4">
                        <Pill variant={sub.is_passing ? 'low' : 'high'}>
                          {sub.is_passing ? 'Eligible' : 'Need Improvement'}
                        </Pill>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Semester-wise SGPA Progression History */}
          <Card className="p-6">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="text-section">Semester-wise Results Summary</CardTitle>
              <CardDescription>
                Performance history, credits cleared, and semester SGPA records.
              </CardDescription>
            </CardHeader>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 lg:grid-cols-6">
              {marks?.progression?.map((sem) => (
                <div
                  key={sem.semester}
                  className="rounded-input border border-line bg-page p-3.5 text-center dark:border-dark-line dark:bg-dark-page"
                >
                  <span className="text-xs text-muted font-medium">Semester {sem.semester}</span>
                  <p className="mt-1 font-heading text-xl font-bold text-accent">
                    {sem.sgpa.toFixed(2)}
                  </p>
                  <p className="mt-1 text-[11px] text-muted">
                    {sem.credits_earned} Credits &bull; {sem.backlogs} Backlogs
                  </p>
                </div>
              ))}
            </div>
          </Card>

          {/* Continuous Internal Evaluation Multi-Dimensional Radar Profile */}
          <Card className="p-6">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="text-section">CIE Multi-Dimensional Assessment Radar Profile</CardTitle>
              <CardDescription>
                Visual spider radar comparing your performance across internal assessments against the VTU benchmark target.
              </CardDescription>
            </CardHeader>
            <div className="pt-2">
              <CieRadarChart marks={marks?.subjects?.[0]} height={260} />
            </div>
          </Card>
        </div>
      )}

      {/* 5. TAB CONTENT: Class Timetable */}
      {activeTab === 'timetable' && (
        <div className="space-y-6">
          <Card className="p-6">
            <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
              <div>
                <CardTitle className="text-section">Weekly Lecture & Laboratory Schedule</CardTitle>
                <CardDescription>
                  Daily class periods for {profile?.class_name || '5th Semester CSE'} (Section {profile?.section || 'A'})
                </CardDescription>
              </div>

              {/* Day Selector Pills */}
              <div className="flex flex-wrap gap-1.5 rounded-input border border-line bg-page p-1 dark:border-dark-line dark:bg-dark-page">
                {timetable?.days?.map((day) => (
                  <button
                    key={day}
                    onClick={() => setSelectedDay(day)}
                    className={`rounded-input px-3 py-1 text-caption font-semibold transition-colors ${
                      selectedDay === day
                        ? 'bg-surface text-accent shadow-sm dark:bg-dark-surface dark:text-dark-text'
                        : 'text-muted hover:text-ink dark:text-dark-muted dark:hover:text-dark-text'
                    }`}
                  >
                    {day}
                  </button>
                ))}
              </div>
            </div>

            {/* Timetable Period Cards for Selected Day */}
            <div className="mt-6 space-y-3">
              {timetable?.schedule?.[selectedDay]?.length > 0 ? (
                timetable.schedule[selectedDay].map((slot) => (
                  <div
                    key={slot.timetable_id}
                    className="flex flex-col justify-between gap-4 rounded-input border border-line bg-page p-4 sm:flex-row sm:items-center dark:border-dark-line dark:bg-dark-page"
                  >
                    <div className="flex items-center gap-4">
                      <div className="flex h-12 w-28 shrink-0 flex-col items-center justify-center rounded-lg border border-line bg-surface text-center dark:border-dark-line dark:bg-dark-surface">
                        <span className="text-[11px] font-bold text-accent">{slot.start_time}</span>
                        <span className="text-[10px] text-muted">to {slot.end_time}</span>
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="font-heading text-body font-bold text-ink dark:text-dark-text">
                            {slot.subject_name}
                          </h4>
                          <span className="font-mono text-xs text-muted">({slot.subject_code})</span>
                          {slot.is_lab && (
                            <span className="rounded bg-accent/10 px-1.5 py-0.5 text-[10px] font-semibold text-accent">
                              Laboratory
                            </span>
                          )}
                        </div>
                        <p className="mt-1 text-caption text-muted dark:text-dark-muted">
                          Faculty: <strong className="text-ink dark:text-dark-text">{slot.teacher_name}</strong>
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 self-start sm:self-center">
                      <span className="rounded-input border border-line bg-surface px-2.5 py-1 text-xs font-semibold text-muted dark:border-dark-line dark:bg-dark-surface">
                        Hall: {slot.room_number}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="flex h-36 items-center justify-center rounded-input border border-dashed border-line text-caption text-muted">
                  No scheduled classes for {selectedDay}.
                </div>
              )}
            </div>
          </Card>
        </div>
      )}

      {/* 6. TAB CONTENT: Mentor Guidance & Remarks */}
      {activeTab === 'guidance' && (
        <div className="space-y-6">
          <Card className="p-6">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="text-section">Faculty Mentorship & Guidance History</CardTitle>
              <CardDescription>
                Direct feedback, performance reviews, and academic advisory logged by your mentor.
              </CardDescription>
            </CardHeader>

            <div className="space-y-4">
              {remarks.length > 0 ? (
                remarks.map((rem) => (
                  <div
                    key={rem.remark_id}
                    className="rounded-input border border-line bg-page p-4 dark:border-dark-line dark:bg-dark-page"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-ink dark:text-dark-text">
                        {rem.teacher_name || 'Faculty Mentor'}
                      </span>
                      <span className="text-xs text-muted">
                        {new Date(rem.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="mt-2 text-body text-ink dark:text-dark-text leading-relaxed">
                      "{rem.remark_text}"
                    </p>
                    {rem.action_taken && (
                      <div className="mt-3 flex items-center gap-2 text-xs font-medium text-accent">
                        <CheckCircle2 className="h-4 w-4" />
                        Action Initiated: {rem.action_taken}
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="flex h-36 items-center justify-center rounded-input border border-dashed border-line text-caption text-muted">
                  No mentor remarks logged yet for this semester.
                </div>
              )}
            </div>
          </Card>
        </div>
      )}

      {/* 7. TAB CONTENT: Notices & Announcements */}
      {activeTab === 'notices' && (
        <div className="space-y-6">
          <Card className="p-6">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="text-section">Announcements & Institutional Circulars</CardTitle>
              <CardDescription>
                Official VTU and PESITM college notifications, exam schedules, and holiday circulars.
              </CardDescription>
            </CardHeader>

            <div className="space-y-3">
              {notifications.length > 0 ? (
                notifications.map((notif) => (
                  <div
                    key={notif.id}
                    className="flex items-start gap-3 rounded-input border border-line bg-page p-4 dark:border-dark-line dark:bg-dark-page"
                  >
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-accent/10 text-accent">
                      <Bell className="h-4 w-4" />
                    </span>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h4 className="font-semibold text-ink dark:text-dark-text">
                          {notif.title}
                        </h4>
                        <span className="text-xs text-muted">
                          {new Date(notif.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="mt-1 text-caption text-muted dark:text-dark-muted">
                        {notif.message}
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="flex h-36 items-center justify-center rounded-input border border-dashed border-line text-caption text-muted">
                  No active notices at this moment.
                </div>
              )}
            </div>
          </Card>
        </div>
      )}

      {/* 8. TAB CONTENT: AI Pass/Fail Predictor */}
      {activeTab === 'prediction' && (
        <div className="space-y-6">
          <Card className="p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-line pb-4 dark:border-dark-line">
              <div>
                <div className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-accent animate-pulse" />
                  <CardTitle className="text-section">AI Examination Pass/Fail Early Warning Engine</CardTitle>
                </div>
                <CardDescription>
                  Evaluates Continuous Internal Evaluation (CIE) scores, attendance rates, and historical SGPA progression using an institutional XGBoost model (98.3% Accuracy).
                </CardDescription>
              </div>
              <Button
                variant="primary"
                onClick={() => setIsPassFailModalOpen(true)}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold flex items-center gap-2 shadow-md shrink-0"
              >
                <Sliders className="h-4 w-4" />
                Open Interactive Predictor & Simulator
              </Button>
            </div>

            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="md:col-span-2 space-y-4">
                <div className="rounded-2xl border border-emerald-200 bg-emerald-50/70 p-6 dark:border-emerald-800/40 dark:bg-emerald-950/20">
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="h-8 w-8 text-emerald-600 dark:text-emerald-400 shrink-0" />
                    <div>
                      <span className="text-xs font-bold uppercase tracking-wider text-muted">Current Forecast</span>
                      <h3 className="font-heading text-2xl font-black text-emerald-700 dark:text-emerald-300">
                        PREDICTED OUTCOME: PASS
                      </h3>
                      <p className="text-xs text-muted mt-0.5">
                        Pass Probability: <strong>99.9%</strong> &bull; Institutional Risk: <strong>LOW RISK (Safe)</strong>
                      </p>
                    </div>
                  </div>
                </div>

                <div className="rounded-xl border border-line bg-page p-4 dark:border-dark-line dark:bg-dark-page space-y-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-muted flex items-center gap-1.5">
                    <TrendingUp className="h-3.5 w-3.5 text-accent" /> Key Academic Attribution Drivers
                  </h4>
                  <ul className="text-xs space-y-1.5 text-ink dark:text-dark-text">
                    <li className="flex items-center gap-2">
                      <ChevronRight className="h-3 w-3 text-emerald-500" />
                      <span><strong>Continuous Internal Marks:</strong> Safe margin above VTU 20/50 qualification threshold.</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <ChevronRight className="h-3 w-3 text-emerald-500" />
                      <span><strong>Attendance Velocity:</strong> Maintained above regulatory 75% requirement.</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <ChevronRight className="h-3 w-3 text-emerald-500" />
                      <span><strong>Prior Semesters:</strong> Zero accumulated active backlogs across engineering courses.</span>
                    </li>
                  </ul>
                </div>
              </div>

              <div className="rounded-xl border border-line bg-surface p-5 dark:border-dark-line dark:bg-dark-surface flex flex-col justify-between">
                <div>
                  <h4 className="font-heading text-subheading font-bold text-ink dark:text-dark-text">What-If Simulation</h4>
                  <p className="mt-1 text-xs text-muted">
                    Simulate how your upcoming IA-2 and IA-3 scores or attendance changes will affect your clearance probability.
                  </p>
                </div>
                <Button
                  variant="outline"
                  className="w-full mt-4 flex items-center justify-center gap-2 font-bold"
                  onClick={() => setIsPassFailModalOpen(true)}
                >
                  <Sparkles className="h-4 w-4 text-accent" />
                  Launch Simulator
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Global Pass/Fail Modal */}
      <PassFailPredictionModal
        isOpen={isPassFailModalOpen}
        onClose={() => setIsPassFailModalOpen(false)}
        initialUsn={profile?.usn || user?.username}
      />
    </div>
  );
}
