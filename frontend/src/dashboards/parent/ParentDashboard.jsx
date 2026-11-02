import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import {
  Users,
  GraduationCap,
  Clock,
  BookOpen,
  Award,
  AlertTriangle,
  CheckCircle2,
  Phone,
  Mail,
  User,
  Sparkles,
  Download,
  CreditCard,
  Send,
  MessageSquare,
  ShieldAlert,
  RefreshCw,
  Calendar,
  ChevronRight,
  Receipt
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
import parentService from '@/services/parentService';

export default function ParentDashboard() {
  const { user } = useAuth();
  const [children, setChildren] = useState([]);
  const [selectedChildId, setSelectedChildId] = useState(null);
  const [childData, setChildData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [childLoading, setChildLoading] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  // Contact Mentor Form State
  const [messageSubject, setMessageSubject] = useState('');
  const [messageBody, setMessageBody] = useState('');
  const [sendingMessage, setSendingMessage] = useState(false);
  const [messageThreads, setMessageThreads] = useState([]);

  // Load Parent's Registered Children
  const loadParentData = async () => {
    setLoading(true);
    try {
      const res = await parentService.getChildren();
      const kids = res.data || [];
      setChildren(kids);

      if (kids.length > 0) {
        // Default to first child or maintain selected
        const currentId = selectedChildId || kids[0].student_id;
        setSelectedChildId(currentId);
        await loadChildDetails(currentId);
      }
      // Load communications
      const msgRes = await parentService.getMessages();
      setMessageThreads(msgRes || []);
    } catch (err) {
      toast.error('Unable to load parent ward profiles.');
    } finally {
      setLoading(false);
    }
  };

  // Load Details for Selected Ward
  const loadChildDetails = async (childId) => {
    setChildLoading(true);
    try {
      const data = await parentService.getChildSummary(childId);
      setChildData(data);
    } catch (err) {
      toast.error('Could not load academic summary for this student.');
    } finally {
      setChildLoading(false);
    }
  };

  useEffect(() => {
    loadParentData();
  }, []);

  const handleChildSelect = async (childId) => {
    setSelectedChildId(childId);
    await loadChildDetails(childId);
  };

  const handleDownloadPdf = async () => {
    if (!selectedChildId || !childData) return;
    setDownloadingPdf(true);
    try {
      await parentService.downloadChildReportPdf(selectedChildId, childData.student?.usn || 'ward');
      toast.success('Ward academic report card downloaded!');
    } catch (err) {
      toast.error('PDF generation failed. Please try again.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!messageBody.trim()) {
      toast.error('Please enter a message for the mentor.');
      return;
    }

    setSendingMessage(true);
    try {
      await parentService.sendMessage({
        studentId: selectedChildId,
        subject: messageSubject || 'Academic Performance Inquiry',
        message: messageBody,
      });
      toast.success('Inquiry transmitted directly to mentor faculty.');
      setMessageSubject('');
      setMessageBody('');
      // Refresh messages
      const msgRes = await parentService.getMessages();
      setMessageThreads(msgRes || []);
    } catch (err) {
      toast.error('Could not send message. Please try again.');
    } finally {
      setSendingMessage(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[500px] flex-col items-center justify-center space-y-4">
        <RefreshCw className="h-8 w-8 animate-spin text-accent" />
        <p className="text-body font-medium text-muted dark:text-dark-muted">
          Loading Parent Academic Portal & Ward Records...
        </p>
      </div>
    );
  }

  const selectedChild = children.find((c) => c.student_id === selectedChildId) || children[0];
  const attendancePct = childData?.attendance?.overall_percentage || selectedChild?.attendance_percentage || 0;
  const isShortage = childData?.attendance?.is_shortage || false;
  const cgpa = childData?.academics?.cgpa || selectedChild?.cgpa || 7.5;
  const backlogs = childData?.academics?.active_backlogs || 0;
  const feeBalance = childData?.finance?.balance_due || 0;
  const feeStatus = childData?.finance?.status || 'Pending';
  const riskLevel = childData?.prediction?.risk_level || selectedChild?.risk_level || 'low';
  const sgpaHistory = childData?.academics?.progression?.map((p) => p.sgpa) || [7.2, 7.4, 7.8, 8.0];

  return (
    <div className="space-y-6">
      {/* 1. Header Banner & Multi-Child Selector */}
      <div className="rounded-card border border-line bg-surface p-6 shadow-sm dark:border-dark-line dark:bg-dark-surface">
        <div className="flex flex-col justify-between gap-6 md:flex-row md:items-center">
          <div>
            <div className="flex items-center gap-2">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/10 text-accent">
                <Users className="h-4 w-4" />
              </span>
              <h1 className="font-heading text-display font-bold text-ink dark:text-dark-text">
                Parent Academic Monitoring Portal
              </h1>
            </div>
            <p className="mt-1 text-body text-muted dark:text-dark-muted">
              PESITM Shivamogga &bull; Centralized academic tracking, ML risk forecasting, and faculty mentor communication.
            </p>
          </div>

          {/* PDF Download Button */}
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => loadChildDetails(selectedChildId)}
              title="Refresh Records"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button
              variant="primary"
              size="md"
              onClick={handleDownloadPdf}
              loading={downloadingPdf}
              className="flex items-center gap-2 whitespace-nowrap shadow-sm"
            >
              <Download className="h-4 w-4" />
              Download Ward Report (PDF)
            </Button>
          </div>
        </div>

        {/* Multi-Child Selector Cards / Pills */}
        {children.length > 1 && (
          <div className="mt-6 border-t border-line pt-4 dark:border-dark-line">
            <span className="text-caption font-semibold uppercase tracking-wider text-muted dark:text-dark-muted">
              Select Enrolled Ward ({children.length} Enrolled):
            </span>
            <div className="mt-2.5 flex flex-wrap gap-3">
              {children.map((child) => {
                const isSelected = child.student_id === selectedChildId;
                return (
                  <button
                    key={child.student_id}
                    onClick={() => handleChildSelect(child.student_id)}
                    className={`flex items-center gap-3 rounded-card border px-4 py-2.5 text-left transition-all ${
                      isSelected
                        ? 'border-accent bg-accent/10 text-accent shadow-sm dark:bg-accent/20'
                        : 'border-line bg-page hover:border-accent/40 dark:border-dark-line dark:bg-dark-page text-ink dark:text-dark-text'
                    }`}
                  >
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent text-white font-heading font-bold text-sm">
                      {child.name.slice(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <strong className="font-heading text-body font-bold text-ink dark:text-dark-text">
                          {child.name}
                        </strong>
                        <span className="font-mono text-xs text-muted">({child.usn})</span>
                      </div>
                      <p className="text-caption text-muted dark:text-dark-muted">
                        {child.relation} &bull; {child.class_name} (Sec {child.section}) &bull; Att: {child.attendance_percentage}%
                      </p>
                    </div>
                    <Pill variant={child.risk_level || 'low'} className="ml-2">
                      {(child.risk_level || 'low').toUpperCase()}
                    </Pill>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Active Ward Profile Strip */}
        <div className="mt-6 flex flex-wrap items-center justify-between gap-4 rounded-input border border-line bg-page p-4 dark:border-dark-line dark:bg-dark-page">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-accent/15 text-accent font-heading font-bold text-lg">
              {childData?.student?.name ? childData.student.name.slice(0, 2).toUpperCase() : 'WD'}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-heading text-section font-bold text-ink dark:text-dark-text">
                  {childData?.student?.name || selectedChild?.name}
                </h3>
                <span className="font-mono text-xs font-semibold text-muted">
                  USN: {childData?.student?.usn || selectedChild?.usn}
                </span>
                <Pill variant={isShortage ? 'high' : 'low'}>
                  {isShortage ? 'Attendance Shortage (<75%)' : 'Attendance Eligible'}
                </Pill>
              </div>
              <p className="mt-0.5 text-caption text-muted dark:text-dark-muted">
                {childData?.student?.department || selectedChild?.department?.dept_name} &bull;{' '}
                {childData?.student?.class_name || selectedChild?.class_name} (Section {childData?.student?.section || selectedChild?.section})
              </p>
            </div>
          </div>

          {/* Mentor Direct Contact Pill */}
          {childData?.student?.mentor && (
            <div className="flex items-center gap-3 rounded-input border border-line bg-surface px-3.5 py-2 text-caption dark:border-dark-line dark:bg-dark-surface">
              <User className="h-4 w-4 text-accent" />
              <div>
                <p className="font-medium text-ink dark:text-dark-text">
                  Mentor: <strong>{childData.student.mentor.name}</strong>
                </p>
                <p className="text-xs text-muted flex items-center gap-2">
                  <Phone className="h-3 w-3" /> {childData.student.mentor.phone}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Shortage Critical Alert */}
        {isShortage && (
          <div className="mt-4 flex items-center gap-3 rounded-input border border-risk-high/30 bg-risk-high/10 p-3.5 text-caption text-risk-high dark:bg-risk-high/20">
            <ShieldAlert className="h-5 w-5 shrink-0" />
            <div>
              <p className="font-semibold">
                VTU Mandatory Shortage Notice: {childData?.student?.name}'s overall attendance is {attendancePct}%.
              </p>
              <p className="mt-0.5 text-xs opacity-90">
                Attendance below 75% results in university semester examination debarment. Please review the breakdown below.
              </p>
            </div>
          </div>
        )}

        {/* Navigation Tabs */}
        <div className="mt-6 flex overflow-x-auto border-t border-line pt-4 scrollbar-none dark:border-dark-line">
          {[
            { id: 'overview', label: 'Ward Trajectory & Risk', icon: Sparkles },
            { id: 'academics', label: 'Internal Marks & SGPA', icon: BookOpen },
            { id: 'attendance', label: 'Attendance Breakdown', icon: Clock },
            { id: 'fees', label: 'College Fees & Receipts', icon: CreditCard },
            { id: 'contact_mentor', label: 'Contact Mentor Faculty', icon: MessageSquare, count: messageThreads.length }
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

      {/* 2. TAB: Overview & ML Risk */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* 4 Metric Cards */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Card className="p-5">
              <div className="flex items-center justify-between">
                <span className="text-caption font-medium text-muted">Overall Attendance</span>
                <span className={`flex h-8 w-8 items-center justify-center rounded-lg ${isShortage ? 'bg-risk-high/10 text-risk-high' : 'bg-risk-low/10 text-risk-low'}`}>
                  <Clock className="h-4 w-4" />
                </span>
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className={`font-heading text-display font-bold ${isShortage ? 'text-risk-high' : 'text-risk-low'}`}>
                  {attendancePct}%
                </span>
                <span className="text-caption text-muted">
                  {childData?.attendance?.total_attended || 0}/{childData?.attendance?.total_held || 0} classes
                </span>
              </div>
              <p className="mt-1 text-xs text-muted">
                {isShortage ? 'Below VTU 75% limit' : 'Meets eligibility requirements'}
              </p>
            </Card>

            <Card className="p-5">
              <div className="flex items-center justify-between">
                <span className="text-caption font-medium text-muted">Cumulative CGPA</span>
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/10 text-accent">
                  <Award className="h-4 w-4" />
                </span>
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="font-heading text-display font-bold text-ink dark:text-dark-text">
                  {cgpa.toFixed(2)}
                </span>
                <span className="text-caption text-muted">/ 10.0</span>
              </div>
              <p className="mt-1 text-xs text-muted">
                {childData?.academics?.total_credits || 100} credits cleared
              </p>
            </Card>

            <Card className="p-5">
              <div className="flex items-center justify-between">
                <span className="text-caption font-medium text-muted">Active Backlogs</span>
                <span className={`flex h-8 w-8 items-center justify-center rounded-lg ${backlogs > 0 ? 'bg-risk-high/10 text-risk-high' : 'bg-risk-low/10 text-risk-low'}`}>
                  <BookOpen className="h-4 w-4" />
                </span>
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="font-heading text-display font-bold text-ink dark:text-dark-text">
                  {backlogs}
                </span>
                <span className="text-caption text-muted">subject(s)</span>
              </div>
              <p className="mt-1 text-xs text-muted">
                {backlogs === 0 ? 'Clear academic standing' : 'Supplementary examinations needed'}
              </p>
            </Card>

            <Card className="p-5">
              <div className="flex items-center justify-between">
                <span className="text-caption font-medium text-muted">Tuition Fee Status</span>
                <span className={`flex h-8 w-8 items-center justify-center rounded-lg ${feeBalance === 0 ? 'bg-risk-low/10 text-risk-low' : 'bg-risk-medium/10 text-risk-medium'}`}>
                  <CreditCard className="h-4 w-4" />
                </span>
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="font-heading text-display font-bold text-ink dark:text-dark-text">
                  ₹{feeBalance.toLocaleString('en-IN')}
                </span>
                <span className="text-caption text-muted">due</span>
              </div>
              <p className="mt-1 text-xs text-muted">
                Status: <strong className={feeBalance === 0 ? 'text-risk-low' : 'text-risk-medium'}>{feeStatus}</strong>
              </p>
            </Card>
          </div>

          {/* ML Risk Gauge & SHAP Drivers */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <Card className="p-6">
              <CardHeader className="p-0 pb-4">
                <CardTitle className="flex items-center gap-2 text-section">
                  <Sparkles className="h-4 w-4 text-accent" />
                  XGBoost Academic Risk Forecast
                </CardTitle>
                <CardDescription>
                  Continuous ML evaluation on student's VTU trajectory.
                </CardDescription>
              </CardHeader>
              <div className="flex flex-col items-center justify-center pt-2">
                <RiskGauge score={childData?.prediction?.risk_score || 0.15} size={220} />
              </div>
            </Card>

            <Card className="p-6 lg:col-span-2">
              <CardHeader className="p-0 pb-4">
                <CardTitle className="flex items-center gap-2 text-section">
                  <Award className="h-4 w-4 text-accent" />
                  SHAP Explainability Vectors
                </CardTitle>
                <CardDescription>
                  Positive drivers promoting success vs factors indicating vulnerability.
                </CardDescription>
              </CardHeader>
              <div className="pt-2">
                <ShapBars explanations={childData?.prediction?.explanations || []} studentName={childData?.student?.name} />
              </div>
            </Card>
          </div>

          {/* Mentor Feedback & Observations */}
          <Card className="p-6">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="flex items-center gap-2 text-section text-accent">
                <MessageSquare className="h-4 w-4" />
                Faculty Mentor Remarks & Remedial Observations
              </CardTitle>
              <CardDescription>
                Direct advisory logged by {childData?.student?.mentor?.name || 'Class Mentor'}.
              </CardDescription>
            </CardHeader>

            <div className="space-y-3">
              {childData?.remarks?.length > 0 ? (
                childData.remarks.map((rem) => (
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
                    <p className="mt-2 text-caption text-ink dark:text-dark-text leading-relaxed">
                      "{rem.remark_text}"
                    </p>
                    {rem.action_taken && (
                      <div className="mt-2 text-xs text-accent font-medium">
                        Action Taken: {rem.action_taken}
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <p className="text-caption text-muted">No remarks recorded for this semester.</p>
              )}
            </div>
          </Card>
        </div>
      )}

      {/* 3. TAB: Academics & CIE */}
      {activeTab === 'academics' && (
        <div className="space-y-6">
          <Card className="p-6">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="text-section">Continuous Internal Evaluation (CIE) Marks</CardTitle>
              <CardDescription>
                Internal assessment test scores and practical assignments (VTU CIE passing criterion: 20/50).
              </CardDescription>
            </CardHeader>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-caption">
                <thead className="border-b border-line bg-page text-muted dark:border-dark-line dark:bg-dark-page">
                  <tr>
                    <th className="py-3 px-4 font-semibold">Subject</th>
                    <th className="py-3 px-4 font-semibold text-center">CIE 1 (30)</th>
                    <th className="py-3 px-4 font-semibold text-center">CIE 2 (30)</th>
                    <th className="py-3 px-4 font-semibold text-center">CIE 3 (30)</th>
                    <th className="py-3 px-4 font-semibold text-center">Assign (10)</th>
                    <th className="py-3 px-4 font-semibold text-center">Quiz (10)</th>
                    <th className="py-3 px-4 font-semibold text-center">Total CIE (50)</th>
                    <th className="py-3 px-4 font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line dark:divide-dark-line">
                  {childData?.academics?.subjects?.map((sub) => (
                    <tr key={sub.marks_id} className="hover:bg-page/50 dark:hover:bg-dark-page/50">
                      <td className="py-3.5 px-4 font-medium text-ink dark:text-dark-text">
                        <span className="font-mono text-xs text-muted block">{sub.subject_code}</span>
                        {sub.subject_name}
                      </td>
                      <td className="py-3.5 px-4 text-center">{sub.cie1}</td>
                      <td className="py-3.5 px-4 text-center">{sub.cie2}</td>
                      <td className="py-3.5 px-4 text-center">{sub.cie3}</td>
                      <td className="py-3.5 px-4 text-center">{sub.assignment}</td>
                      <td className="py-3.5 px-4 text-center">{sub.quiz}</td>
                      <td className="py-3.5 px-4 text-center font-heading text-body font-bold text-ink dark:text-dark-text">
                        {sub.total_cie}
                      </td>
                      <td className="py-3.5 px-4">
                        <Pill variant={sub.is_passing ? 'low' : 'high'}>
                          {sub.is_passing ? 'Passing' : 'Critical'}
                        </Pill>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* SGPA Trend */}
          <Card className="p-6">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="text-section">Semester SGPA Trajectory</CardTitle>
              <CardDescription>Historical progression across previous university semesters.</CardDescription>
            </CardHeader>
            <div className="pt-2">
              <SgpaTrend history={sgpaHistory} targetGpa={7.0} height={220} />
            </div>
          </Card>

          {/* CIE Radar Multi-Dimensional Assessment Profile */}
          <Card className="p-6">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="text-section">Continuous Evaluation Assessment Profile</CardTitle>
              <CardDescription>
                Radar visualization displaying your child's performance across internal test scores vs benchmark targets.
              </CardDescription>
            </CardHeader>
            <div className="pt-2">
              <CieRadarChart marks={childData?.academics?.subjects?.[0]} height={250} />
            </div>
          </Card>
        </div>
      )}

      {/* 4. TAB: Attendance Breakdown */}
      {activeTab === 'attendance' && (
        <div className="space-y-6">
          <Card className="p-6">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="text-section">Subject-wise Class Attendance</CardTitle>
              <CardDescription>
                Minimum VTU requirement is 75% attendance in each registered theory and laboratory course.
              </CardDescription>
            </CardHeader>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-caption">
                <thead className="border-b border-line bg-page text-muted dark:border-dark-line dark:bg-dark-page">
                  <tr>
                    <th className="py-3 px-4 font-semibold">Subject</th>
                    <th className="py-3 px-4 font-semibold text-center">Attended / Total</th>
                    <th className="py-3 px-4 font-semibold text-center">Percentage</th>
                    <th className="py-3 px-4 font-semibold">Eligibility</th>
                    <th className="py-3 px-4 font-semibold">Required Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line dark:divide-dark-line">
                  {childData?.attendance?.subjects?.map((sub) => (
                    <tr key={sub.attendance_id} className="hover:bg-page/50 dark:hover:bg-dark-page/50">
                      <td className="py-3.5 px-4 font-medium text-ink dark:text-dark-text">
                        <span className="font-mono text-xs text-muted block">{sub.subject_code}</span>
                        {sub.subject_name}
                      </td>
                      <td className="py-3.5 px-4 text-center text-muted">
                        {sub.attended_classes} / {sub.total_classes}
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <span className={`font-heading font-bold ${sub.is_shortage ? 'text-risk-high' : 'text-risk-low'}`}>
                          {sub.percentage}%
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <Pill variant={sub.is_shortage ? 'high' : 'low'}>
                          {sub.is_shortage ? 'Shortage (<75%)' : 'Eligible'}
                        </Pill>
                      </td>
                      <td className="py-3.5 px-4 text-xs">
                        {sub.is_shortage ? (
                          <span className="text-risk-high font-medium">
                            Requires {sub.classes_needed} consecutive attendance(s) to clear
                          </span>
                        ) : (
                          <span className="text-risk-low font-medium">Good standing</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Visual Subject Attendance Bar Chart */}
          <Card className="p-6">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="text-section">Visual Subject Attendance & Compliance Meter</CardTitle>
              <CardDescription>
                Graphical comparison of your child's attendance against the VTU 75% minimum threshold.
              </CardDescription>
            </CardHeader>
            <div className="pt-2">
              <AttendanceBar subjects={childData?.attendance?.subjects || []} height={250} />
            </div>
          </Card>
        </div>
      )}

      {/* 5. TAB: College Fees & Receipts */}
      {activeTab === 'fees' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <Card className="p-4">
              <span className="text-caption font-medium text-muted">Total Annual Tuition Fee</span>
              <p className="mt-1 font-heading text-2xl font-bold text-ink dark:text-dark-text">
                ₹{(childData?.finance?.total_annual_fee || 85000).toLocaleString('en-IN')}
              </p>
            </Card>
            <Card className="p-4">
              <span className="text-caption font-medium text-muted">Amount Paid</span>
              <p className="mt-1 font-heading text-2xl font-bold text-risk-low">
                ₹{(childData?.finance?.amount_paid || 0).toLocaleString('en-IN')}
              </p>
            </Card>
            <Card className="p-4">
              <span className="text-caption font-medium text-muted">Balance Due</span>
              <p className={`mt-1 font-heading text-2xl font-bold ${feeBalance > 0 ? 'text-risk-medium' : 'text-risk-low'}`}>
                ₹{feeBalance.toLocaleString('en-IN')}
              </p>
            </Card>
          </div>

          <Card className="p-6">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="text-section">Payment Receipts & Transaction Log</CardTitle>
              <CardDescription>Official transaction records acknowledged by the Accounts Office.</CardDescription>
            </CardHeader>

            <div className="space-y-3">
              {childData?.finance?.payments?.length > 0 ? (
                childData.finance.payments.map((p) => (
                  <div
                    key={p.payment_id}
                    className="flex flex-col justify-between gap-2 rounded-input border border-line bg-page p-3.5 sm:flex-row sm:items-center dark:border-dark-line dark:bg-dark-page"
                  >
                    <div className="flex items-center gap-3">
                      <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-risk-low/10 text-risk-low">
                        <Receipt className="h-4 w-4" />
                      </span>
                      <div>
                        <p className="font-semibold text-ink dark:text-dark-text">
                          ₹{p.amount_paid.toLocaleString('en-IN')} &bull; {p.payment_mode}
                        </p>
                        <p className="font-mono text-xs text-muted">Ref: {p.transaction_reference}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-muted">
                        {new Date(p.payment_date).toLocaleDateString()}
                      </span>
                      <Pill variant="low">Completed</Pill>
                    </div>
                  </div>
                ))
              ) : (
                <div className="flex h-32 items-center justify-center rounded-input border border-dashed border-line text-caption text-muted">
                  No payment receipts recorded for this academic year.
                </div>
              )}
            </div>
          </Card>
        </div>
      )}

      {/* 6. TAB: Contact Mentor Faculty */}
      {activeTab === 'contact_mentor' && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Message Compose Form */}
          <Card className="p-6 lg:col-span-2">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="text-section">Send Communication to Faculty Mentor</CardTitle>
              <CardDescription>
                Direct inquiry to {childData?.student?.mentor?.name || 'Class Mentor'} regarding attendance, CIE marks, or student support.
              </CardDescription>
            </CardHeader>

            <form onSubmit={handleSendMessage} className="space-y-4 pt-2">
              <div>
                <label className="block text-caption font-semibold text-ink dark:text-dark-text">
                  Inquiry Subject
                </label>
                <input
                  type="text"
                  value={messageSubject}
                  onChange={(e) => setMessageSubject(e.target.value)}
                  placeholder="e.g., Discussion regarding CIE 2 preparation or attendance shortage"
                  className="mt-1.5 w-full rounded-input border border-line bg-surface px-3.5 py-2 text-caption text-ink placeholder:text-muted/60 focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                />
              </div>

              <div>
                <label className="block text-caption font-semibold text-ink dark:text-dark-text">
                  Your Message
                </label>
                <textarea
                  rows={4}
                  value={messageBody}
                  onChange={(e) => setMessageBody(e.target.value)}
                  placeholder="Dear Professor, I would like to inquire about my ward's progress..."
                  className="mt-1.5 w-full rounded-input border border-line bg-surface p-3.5 text-caption text-ink placeholder:text-muted/60 focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                  required
                />
              </div>

              <div className="flex justify-end">
                <Button
                  type="submit"
                  variant="primary"
                  loading={sendingMessage}
                  className="flex items-center gap-2"
                >
                  <Send className="h-4 w-4" />
                  Dispatch Inquiry to Mentor
                </Button>
              </div>
            </form>
          </Card>

          {/* Previous Communications Sidebar */}
          <Card className="p-6">
            <CardHeader className="p-0 pb-3">
              <CardTitle className="text-caption font-bold uppercase tracking-wider text-muted">
                Recent Inquiries & Replies
              </CardTitle>
            </CardHeader>

            <div className="space-y-3 pt-1">
              {messageThreads.length > 0 ? (
                messageThreads.slice(0, 5).map((m) => (
                  <div
                    key={m.id}
                    className="rounded-input border border-line bg-page p-3 text-caption dark:border-dark-line dark:bg-dark-page"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-ink dark:text-dark-text truncate">
                        {m.title}
                      </span>
                      <span className="text-[10px] text-muted">
                        {new Date(m.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="mt-1 text-xs text-muted line-clamp-2">{m.message}</p>
                  </div>
                ))
              ) : (
                <p className="text-caption text-muted">No prior inquiries recorded.</p>
              )}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
