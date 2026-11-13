import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import {
  BookOpen,
  Users,
  Clock,
  Sparkles,
  Sliders,
  AlertTriangle,
  CheckCircle2,
  Search,
  Filter,
  Edit3,
  History,
  MessageSquare,
  Upload,
  Send,
  RefreshCw,
  FileSpreadsheet,
  ShieldAlert,
  ChevronRight,
  UserCheck,
  UserX,
  X,
  FileDown,
  Save,
  ShieldCheck,
  Check
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Pill } from '@/components/ui/Pill';
import { Modal } from '@/components/ui/Modal';
import { useAuth } from '@/context/AuthContext';
import teacherService from '@/services/teacherService';
import PassFailPredictionModal from '@/components/predictions/PassFailPredictionModal';

export default function TeacherDashboard() {
  const { user } = useAuth();
  const [classes, setClasses] = useState([]);
  const [selectedAssignment, setSelectedAssignment] = useState(null);
  const [roster, setRoster] = useState([]);
  const [loading, setLoading] = useState(true);
  const [rosterLoading, setRosterLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('roster');
  const [selectedStudentUsnForPrediction, setSelectedStudentUsnForPrediction] = useState(null);
  const [isTeacherPredictionModalOpen, setIsTeacherPredictionModalOpen] = useState(false);

  // Filters & Search
  const [searchQuery, setSearchQuery] = useState('');
  const [riskFilter, setRiskFilter] = useState('all');

  // Single Student Edit Marks Modal state
  const [editingStudent, setEditingStudent] = useState(null);
  const [marksForm, setMarksForm] = useState({ cie1: '', cie2: '', cie3: '', assignment_marks: '', quiz_marks: '', reason: '' });
  const [updatingMarks, setUpdatingMarks] = useState(false);

  // Single Student History Modal
  const [historyStudent, setHistoryStudent] = useState(null);
  const [marksHistory, setMarksHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  // Single Student Remark Modal
  const [remarkStudent, setRemarkStudent] = useState(null);
  const [remarkText, setRemarkText] = useState('');
  const [actionTaken, setActionTaken] = useState('');
  const [savingRemark, setSavingRemark] = useState(false);

  // Attendance Session State
  const [sessionDate, setSessionDate] = useState(new Date().toISOString().split('T')[0]);
  const [sessionAttendance, setSessionAttendance] = useState({});
  const [submittingAttendance, setSubmittingAttendance] = useState(false);

  // Batch CSV Upload State
  const [uploadType, setUploadType] = useState('marks');
  const [csvFile, setCsvFile] = useState(null);
  const [uploadingCsv, setUploadingCsv] = useState(false);
  const [uploadResults, setUploadResults] = useState(null);

  // Broadcast Notification State
  const [broadcastTarget, setBroadcastTarget] = useState('all');
  const [selectedStudentIds, setSelectedStudentIds] = useState([]);
  const [broadcastSubject, setBroadcastSubject] = useState('');
  const [broadcastMessage, setBroadcastMessage] = useState('');
  const [forwardToParents, setForwardToParents] = useState(true);
  const [broadcasting, setBroadcasting] = useState(false);

  // PHASE 10: Bulk Matrix CIE State
  const [bulkMarksData, setBulkMarksData] = useState({});
  const [isBulkSaveOpen, setIsBulkSaveOpen] = useState(false);
  const [bulkSaveReason, setBulkSaveReason] = useState('');
  const [savingBulkMarks, setSavingBulkMarks] = useState(false);

  // PHASE 10: Class Audit Trail Inspector State
  const [classAuditHistory, setClassAuditHistory] = useState([]);
  const [loadingAuditHistory, setLoadingAuditHistory] = useState(false);

  // PHASE 10: Attendance Direct Adjustment State
  const [editingAttendanceStudent, setEditingAttendanceStudent] = useState(null);
  const [attendanceForm, setAttendanceForm] = useState({ total_classes: 0, attended_classes: 0, reason: '' });
  const [updatingAttendance, setUpdatingAttendance] = useState(false);

  // Live VTU Total Calculation: Best 2 of 3 CIE tests average + Assignment + Quiz
  const calculateLiveVtuTotal = (cie1, cie2, cie3, assign, quiz) => {
    const tests = [
      parseFloat(cie1) || 0,
      parseFloat(cie2) || 0,
      parseFloat(cie3) || 0
    ].sort((a, b) => b - a);
    const top2Avg = (tests[0] + tests[1]) / 2.0;
    return parseFloat((top2Avg + (parseFloat(assign) || 0) + (parseFloat(quiz) || 0)).toFixed(2));
  };

  // Load teacher assigned classes
  const loadClasses = async () => {
    setLoading(true);
    try {
      const res = await teacherService.getAssignedClasses();
      const list = res.data || [];
      setClasses(list);
      if (list.length > 0) {
        const first = list[0];
        setSelectedAssignment(first);
        await loadRoster(first.class_id, first.subject_id);
      }
    } catch (err) {
      toast.error('Could not load assigned teaching allocations.');
    } finally {
      setLoading(false);
    }
  };

  // Load roster for assigned unit
  const loadRoster = async (classId, subjectId) => {
    setRosterLoading(true);
    try {
      const res = await teacherService.getClassRoster(classId, { subject_id: subjectId });
      const students = res.data || [];
      setRoster(students);

      // Initialize session attendance state to all present by default
      const initialAtt = {};
      const initialBulk = {};

      students.forEach((s) => {
        initialAtt[s.student_id] = true;
        initialBulk[s.student_id] = {
          cie1: s.marks?.cie1 !== undefined ? s.marks.cie1 : 0,
          cie2: s.marks?.cie2 !== undefined ? s.marks.cie2 : 0,
          cie3: s.marks?.cie3 !== undefined ? s.marks.cie3 : 0,
          assignment_marks: s.marks?.assignment_marks !== undefined ? s.marks.assignment_marks : 0,
          quiz_marks: s.marks?.quiz_marks !== undefined ? s.marks.quiz_marks : 0,
          total_cie: s.marks?.total_cie !== undefined ? s.marks.total_cie : 0,
        };
      });

      setSessionAttendance(initialAtt);
      setBulkMarksData(initialBulk);
    } catch (err) {
      toast.error('Failed to load class student roster.');
    } finally {
      setRosterLoading(false);
    }
  };

  useEffect(() => {
    loadClasses();
  }, []);

  const handleSelectAssignment = async (assign) => {
    setSelectedAssignment(assign);
    await loadRoster(assign.class_id, assign.subject_id);
    if (activeTab === 'audit_history') {
      loadClassAuditHistory(assign.class_id, assign.subject_id);
    }
  };

  // Load Class Audit History
  const loadClassAuditHistory = async (cId = null, sId = null) => {
    const classId = cId || selectedAssignment?.class_id;
    const subjectId = sId || selectedAssignment?.subject_id;
    if (!classId || !subjectId) return;

    setLoadingAuditHistory(true);
    try {
      const data = await teacherService.getClassSubjectAuditHistory(classId, subjectId);
      setClassAuditHistory(data || []);
    } catch (err) {
      console.error('Error loading audit history:', err);
    } finally {
      setLoadingAuditHistory(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'audit_history') {
      loadClassAuditHistory();
    }
  }, [activeTab]);

  // Filtered Roster
  const filteredRoster = roster.filter((s) => {
    const matchesSearch =
      searchQuery === '' ||
      s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.usn.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRisk =
      riskFilter === 'all' || s.prediction?.risk_level?.toLowerCase() === riskFilter.toLowerCase();
    return matchesSearch && matchesRisk;
  });

  // Open Edit Marks Modal
  const handleOpenEditMarks = (student) => {
    setEditingStudent(student);
    setMarksForm({
      cie1: student.marks?.cie1 || '',
      cie2: student.marks?.cie2 || '',
      cie3: student.marks?.cie3 || '',
      assignment_marks: student.marks?.assignment_marks || '',
      quiz_marks: student.marks?.quiz_marks || '',
      reason: ''
    });
  };

  // Save Edit Marks (Single)
  const handleSaveMarks = async (e) => {
    e.preventDefault();
    if (!marksForm.reason.trim()) {
      toast.error('A justification reason is mandatory for marks alterations.');
      return;
    }
    setUpdatingMarks(true);
    try {
      await teacherService.updateMarks(editingStudent.marks.marks_id, marksForm);
      toast.success(`Marks successfully updated for ${editingStudent.name}.`);
      setEditingStudent(null);
      await loadRoster(selectedAssignment.class_id, selectedAssignment.subject_id);
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to update marks.');
    } finally {
      setUpdatingMarks(false);
    }
  };

  // Open History Modal
  const handleOpenHistory = async (student) => {
    setHistoryStudent(student);
    setHistoryLoading(true);
    try {
      const data = await teacherService.getMarksHistory(student.marks.marks_id);
      setMarksHistory(data || []);
    } catch (err) {
      toast.error('Could not load modification audit history.');
    } finally {
      setHistoryLoading(false);
    }
  };

  // Open Attendance Override Modal
  const handleOpenEditAttendance = (student) => {
    setEditingAttendanceStudent(student);
    setAttendanceForm({
      total_classes: student.attendance?.total_classes || 0,
      attended_classes: student.attendance?.attended_classes || 0,
      reason: ''
    });
  };

  // Save Attendance Override
  const handleSaveAttendance = async (e) => {
    e.preventDefault();
    if (!attendanceForm.reason.trim()) {
      toast.error('Justification reason is strictly mandatory for attendance overrides.');
      return;
    }
    setUpdatingAttendance(true);
    try {
      await teacherService.updateAttendanceRecord(editingAttendanceStudent.attendance.attendance_id, attendanceForm);
      toast.success(`Attendance updated for ${editingAttendanceStudent.name}.`);
      setEditingAttendanceStudent(null);
      await loadRoster(selectedAssignment.class_id, selectedAssignment.subject_id);
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to update attendance record.');
    } finally {
      setUpdatingAttendance(false);
    }
  };

  // Save Remark
  const handleSaveRemark = async (e) => {
    e.preventDefault();
    setSavingRemark(true);
    try {
      await teacherService.addRemark({
        studentId: remarkStudent.student_id,
        remarkText,
        actionTaken
      });
      toast.success('Mentorship remark recorded.');
      setRemarkStudent(null);
      setRemarkText('');
      setActionTaken('');
    } catch (err) {
      toast.error('Failed to log remark.');
    } finally {
      setSavingRemark(false);
    }
  };

  // Attendance mass actions
  const handleMarkAllPresent = () => {
    const updated = {};
    roster.forEach((s) => { updated[s.student_id] = true; });
    setSessionAttendance(updated);
    toast.success('Marked all students Present.');
  };

  const handleMarkAllAbsent = () => {
    const updated = {};
    roster.forEach((s) => { updated[s.student_id] = false; });
    setSessionAttendance(updated);
    toast.success('Marked all students Absent.');
  };

  const handleInvertAttendance = () => {
    const updated = {};
    roster.forEach((s) => {
      updated[s.student_id] = !sessionAttendance[s.student_id];
    });
    setSessionAttendance(updated);
  };

  // Submit Session Attendance
  const handleSubmitAttendance = async () => {
    if (!selectedAssignment) return;
    setSubmittingAttendance(true);
    try {
      const list = Object.entries(sessionAttendance).map(([studentId, isPresent]) => ({
        student_id: parseInt(studentId, 10),
        is_present: isPresent
      }));

      const res = await teacherService.logAttendance({
        classId: selectedAssignment.class_id,
        subjectId: selectedAssignment.subject_id,
        date: sessionDate,
        attendanceList: list
      });

      toast.success(res.message || 'Session attendance logged successfully.');
      await loadRoster(selectedAssignment.class_id, selectedAssignment.subject_id);
      setActiveTab('roster');
    } catch (err) {
      toast.error('Failed to log attendance session.');
    } finally {
      setSubmittingAttendance(false);
    }
  };

  // Live Bulk Marks Handlers
  const handleBulkMarksChange = (studentId, field, value) => {
    setBulkMarksData((prev) => {
      const current = prev[studentId] || {};
      const updated = { ...current, [field]: value };
      updated.total_cie = calculateLiveVtuTotal(
        updated.cie1,
        updated.cie2,
        updated.cie3,
        updated.assignment_marks,
        updated.quiz_marks
      );
      return { ...prev, [studentId]: updated };
    });
  };

  // Submit Bulk Marks with Mandatory Reason
  const handleSaveBulkMarks = async (e) => {
    e.preventDefault();
    if (!bulkSaveReason.trim()) {
      toast.error('Justification reason is strictly mandatory for institutional audit.');
      return;
    }
    setSavingBulkMarks(true);
    try {
      const marksPayload = Object.entries(bulkMarksData).map(([studentId, data]) => ({
        student_id: parseInt(studentId, 10),
        cie1: parseFloat(data.cie1) || 0.0,
        cie2: parseFloat(data.cie2) || 0.0,
        cie3: parseFloat(data.cie3) || 0.0,
        assignment_marks: parseFloat(data.assignment_marks) || 0.0,
        quiz_marks: parseFloat(data.quiz_marks) || 0.0,
      }));

      const res = await teacherService.bulkUpdateMarks({
        class_id: selectedAssignment.class_id,
        subject_id: selectedAssignment.subject_id,
        reason: bulkSaveReason.trim(),
        marks: marksPayload,
      });

      toast.success(res.message || 'Bulk marks successfully recorded.');
      setIsBulkSaveOpen(false);
      setBulkSaveReason('');
      await loadRoster(selectedAssignment.class_id, selectedAssignment.subject_id);
      loadClassAuditHistory();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to save bulk marks.');
    } finally {
      setSavingBulkMarks(false);
    }
  };

  // Download Templates
  const handleDownloadMarksTemplate = async () => {
    if (!selectedAssignment) return;
    try {
      toast.loading('Generating Marks CSV Template...', { id: 'csv-dl' });
      await teacherService.downloadMarksTemplate(selectedAssignment.class_id, selectedAssignment.subject_id);
      toast.success('Marks Template downloaded.', { id: 'csv-dl' });
    } catch (err) {
      toast.error('Failed to download marks template.', { id: 'csv-dl' });
    }
  };

  const handleDownloadAttendanceTemplate = async () => {
    if (!selectedAssignment) return;
    try {
      toast.loading('Generating Attendance CSV Template...', { id: 'csv-dl' });
      await teacherService.downloadAttendanceTemplate(selectedAssignment.class_id, selectedAssignment.subject_id);
      toast.success('Attendance Template downloaded.', { id: 'csv-dl' });
    } catch (err) {
      toast.error('Failed to download attendance template.', { id: 'csv-dl' });
    }
  };

  // Submit Batch CSV
  const handleUploadCsv = async (e) => {
    e.preventDefault();
    if (!csvFile) {
      toast.error('Please select a CSV file to upload.');
      return;
    }

    setUploadingCsv(true);
    setUploadResults(null);
    try {
      const formData = new FormData();
      formData.append('file', csvFile);
      formData.append('class_id', selectedAssignment.class_id);
      formData.append('subject_id', selectedAssignment.subject_id);
      formData.append('upload_type', uploadType);

      const res = await teacherService.uploadCsv(formData);
      setUploadResults(res);
      toast.success(`Batch processed: ${res.processed_count} rows ingested.`);
      await loadRoster(selectedAssignment.class_id, selectedAssignment.subject_id);
    } catch (err) {
      toast.error(err.response?.data?.message || 'CSV Ingestion failed.');
    } finally {
      setUploadingCsv(false);
    }
  };

  // Broadcast Notice
  const handleBroadcastNotice = async (e) => {
    e.preventDefault();
    if (!broadcastSubject || !broadcastMessage) {
      toast.error('Subject and message content are required.');
      return;
    }

    setBroadcasting(true);
    try {
      const res = await teacherService.notifyStudents({
        classId: selectedAssignment.class_id,
        studentIds: broadcastTarget === 'all' ? [] : selectedStudentIds,
        subject: broadcastSubject,
        message: broadcastMessage,
        sendToParent: forwardToParents
      });
      toast.success(res.message || 'Notice transmitted to students.');
      setBroadcastSubject('');
      setBroadcastMessage('');
    } catch (err) {
      toast.error('Failed to dispatch notices.');
    } finally {
      setBroadcasting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center gap-3">
        <RefreshCw className="h-8 w-8 animate-spin text-accent" />
        <p className="text-body font-medium text-muted dark:text-dark-muted">
          Loading faculty assignments, class telemetry & roster...
        </p>
      </div>
    );
  }

  const metrics = selectedAssignment?.metrics || {
    total_students: 0,
    average_attendance: 0,
    shortage_count: 0,
    average_cie: 0,
    at_risk_count: 0
  };

  const totalPresentCount = Object.values(sessionAttendance).filter(Boolean).length;
  const totalAbsentCount = roster.length - totalPresentCount;

  return (
    <div className="space-y-6">
      {/* 1. Header Banner & Class Teaching Unit Switcher */}
      <div className="rounded-card border border-line bg-surface p-6 shadow-sm dark:border-dark-line dark:bg-dark-surface">
        <div className="flex flex-col justify-between gap-6 md:flex-row md:items-center">
          <div>
            <div className="flex items-center gap-2">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/10 text-accent">
                <BookOpen className="h-4 w-4" />
              </span>
              <h1 className="font-heading text-display font-bold text-ink dark:text-dark-text">
                Faculty & Mentor Operations Portal
              </h1>
            </div>
            <p className="mt-1 text-body text-muted dark:text-dark-muted">
              PESITM Shivamogga &bull; Continuous assessment audit trails, attendance monitoring & student intervention.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => selectedAssignment && loadRoster(selectedAssignment.class_id, selectedAssignment.subject_id)}
              title="Refresh Roster"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button
              variant="primary"
              size="md"
              onClick={() => {
                setSelectedStudentUsnForPrediction(null);
                setIsTeacherPredictionModalOpen(true);
              }}
              className="flex items-center gap-2 whitespace-nowrap bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-700 hover:to-purple-700 text-white shadow-md font-bold"
            >
              <Sparkles className="h-4 w-4 animate-pulse text-amber-300" />
              Predict Class Pass / Fail
            </Button>
          </div>
        </div>

        {/* Assigned Teaching Units Selector */}
        <div className="mt-6 border-t border-line pt-4 dark:border-dark-line">
          <span className="text-caption font-semibold uppercase tracking-wider text-muted dark:text-dark-muted">
            Assigned Instructional Units ({classes.length} Active):
          </span>
          <div className="mt-2.5 flex flex-wrap gap-3">
            {classes.map((assign) => {
              const isSelected = selectedAssignment?.assignment_id === assign.assignment_id;
              return (
                <button
                  key={assign.assignment_id}
                  onClick={() => handleSelectAssignment(assign)}
                  className={`flex items-center gap-3 rounded-card border px-4 py-2.5 text-left transition-all ${
                    isSelected
                      ? 'border-accent bg-accent/10 text-accent shadow-sm dark:bg-accent/20'
                      : 'border-line bg-page hover:border-accent/40 dark:border-dark-line dark:bg-dark-page text-ink dark:text-dark-text'
                  }`}
                >
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent text-white font-mono font-bold text-xs">
                    {assign.subject_code.slice(0, 4)}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <strong className="font-heading text-body font-bold text-ink dark:text-dark-text">
                        {assign.class_name} (Sec {assign.section})
                      </strong>
                      {assign.is_mentor && (
                        <span className="rounded bg-accent/15 px-1.5 py-0.5 text-[10px] font-semibold text-accent">
                          Class Mentor
                        </span>
                      )}
                    </div>
                    <p className="text-caption text-muted dark:text-dark-muted">
                      {assign.subject_name} &bull; {assign.metrics.total_students} Students
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Live Operational Class KPIs */}
        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Card className="p-4 bg-page/60 dark:bg-dark-page/60 border-line">
            <span className="text-caption font-medium text-muted">Total Enrolled</span>
            <p className="mt-1 font-heading text-2xl font-bold text-ink dark:text-dark-text">
              {metrics.total_students}
            </p>
            <p className="mt-0.5 text-xs text-muted">Active VTU cohort</p>
          </Card>

          <Card className="p-4 bg-page/60 dark:bg-dark-page/60 border-line">
            <span className="text-caption font-medium text-muted">Average Attendance</span>
            <p className="mt-1 font-heading text-2xl font-bold text-ink dark:text-dark-text">
              {metrics.average_attendance}%
            </p>
            <p className="mt-0.5 text-xs text-risk-high font-medium">
              {metrics.shortage_count} students with shortage (&lt;75%)
            </p>
          </Card>

          <Card className="p-4 bg-page/60 dark:bg-dark-page/60 border-line">
            <span className="text-caption font-medium text-muted">Average CIE Score</span>
            <p className="mt-1 font-heading text-2xl font-bold text-accent">
              {metrics.average_cie} / 50.0
            </p>
            <p className="mt-0.5 text-xs text-muted">VTU benchmark passing: 20/50</p>
          </Card>

          <Card className="p-4 bg-page/60 dark:bg-dark-page/60 border-line">
            <span className="text-caption font-medium text-muted">At-Risk Students</span>
            <div className="mt-1 flex items-baseline gap-2">
              <span className={`font-heading text-2xl font-bold ${metrics.at_risk_count > 0 ? 'text-risk-high' : 'text-risk-low'}`}>
                {metrics.at_risk_count}
              </span>
              <span className="text-xs text-muted">students</span>
            </div>
            <p className="mt-0.5 text-xs text-muted">High & Medium XGBoost risk</p>
          </Card>
        </div>

        {/* Action Tabs Navigation */}
        <div className="mt-6 flex overflow-x-auto border-t border-line pt-4 scrollbar-none dark:border-dark-line">
          {[
            { id: 'roster', label: 'Class Roster & Telemetry', icon: Users, count: roster.length },
            { id: 'pass_fail_analytics', label: 'Class Pass/Fail Analytics', icon: Sparkles },
            { id: 'bulk_cie', label: 'Bulk Matrix CIE Entry', icon: FileSpreadsheet },
            { id: 'attendance_session', label: 'Log Session Attendance', icon: Clock },
            { id: 'audit_history', label: 'Marks Audit Trail Inspector', icon: History, count: classAuditHistory.length || undefined },
            { id: 'batch_upload', label: 'Batch CSV Ingest', icon: Upload },
            { id: 'broadcast', label: 'Notice Dispatcher', icon: Send }
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
                {tab.count !== undefined && (
                  <span className="rounded-pill bg-line px-1.5 py-0.5 text-[10px] text-muted dark:bg-dark-line">
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* 2. TAB: Roster & Student Telemetry */}
      {activeTab === 'roster' && (
        <Card className="p-6">
          <CardHeader className="p-0 pb-4">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <CardTitle className="text-section">
                  Class Student Roster & Academic Records
                </CardTitle>
                <CardDescription>
                  Review individual continuous assessment marks, attendance levels, and ML risk predictions.
                </CardDescription>
              </div>

              {/* Roster Controls */}
              <div className="flex flex-wrap items-center gap-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted" />
                  <input
                    type="text"
                    placeholder="Search USN or Name..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-48 rounded-input border border-line bg-page py-1.5 pl-8 pr-3 text-caption text-ink placeholder:text-muted focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-page dark:text-dark-text"
                  />
                </div>

                <select
                  value={riskFilter}
                  onChange={(e) => setRiskFilter(e.target.value)}
                  className="rounded-input border border-line bg-page px-3 py-1.5 text-caption font-medium text-ink focus:outline-none dark:border-dark-line dark:bg-dark-page dark:text-dark-text"
                >
                  <option value="all">All Risk Levels</option>
                  <option value="high">High Risk Only</option>
                  <option value="medium">Medium Risk</option>
                  <option value="low">Low Risk</option>
                </select>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleDownloadMarksTemplate}
                  title="Download Pre-filled Marks CSV Template"
                  className="flex items-center gap-1.5"
                >
                  <FileDown className="h-4 w-4" />
                  <span>Marks Template</span>
                </Button>
              </div>
            </div>
          </CardHeader>

          {/* Roster Table */}
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-caption">
              <thead className="border-b border-line bg-page text-muted dark:border-dark-line dark:bg-dark-page">
                <tr>
                  <th className="py-3 px-4 font-semibold">USN</th>
                  <th className="py-3 px-4 font-semibold">Student Name</th>
                  <th className="py-3 px-4 font-semibold text-center">Attendance %</th>
                  <th className="py-3 px-4 font-semibold text-center">CIE Marks (50)</th>
                  <th className="py-3 px-4 font-semibold text-center">ML Risk Forecast</th>
                  <th className="py-3 px-4 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line dark:divide-dark-line">
                {rosterLoading ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-muted">
                      <RefreshCw className="mx-auto h-6 w-6 animate-spin text-accent" />
                      <span className="mt-2 block">Loading student telemetry...</span>
                    </td>
                  </tr>
                ) : filteredRoster.length > 0 ? (
                  filteredRoster.map((s) => {
                    const att = s.attendance;
                    const marks = s.marks;
                    const pred = s.prediction;
                    const isShortage = att.is_shortage;

                    return (
                      <tr key={s.student_id} className="hover:bg-page/50 dark:hover:bg-dark-page/50 transition-colors">
                        <td className="py-3.5 px-4 font-mono font-semibold text-ink dark:text-dark-text">
                          {s.usn}
                        </td>
                        <td className="py-3.5 px-4 font-medium text-ink dark:text-dark-text">
                          {s.name}
                        </td>
                        <td className="py-3.5 px-4 text-center">
                          <button
                            onClick={() => handleOpenEditAttendance(s)}
                            className="group flex flex-col items-center mx-auto hover:opacity-80 transition-opacity"
                            title="Click to adjust attendance figure"
                          >
                            <span className={`font-heading font-bold ${isShortage ? 'text-risk-high' : 'text-risk-low'}`}>
                              {att.percentage}%
                            </span>
                            <span className="text-xs text-muted group-hover:text-accent">
                              {att.attended_classes}/{att.total_classes} (Edit)
                            </span>
                          </button>
                        </td>
                        <td className="py-3.5 px-4 text-center font-heading text-body font-bold text-ink dark:text-dark-text">
                          {marks.total_cie}
                          <span className="text-[10px] text-muted block font-normal">
                            C1:{marks.cie1} C2:{marks.cie2} C3:{marks.cie3}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-center">
                          <Pill variant={pred.risk_level || 'low'}>
                            {(pred.risk_level || 'low').toUpperCase()} ({Math.round(pred.risk_score * 100)}%)
                          </Pill>
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <div className="flex items-center justify-end gap-1.5">
                            <Button
                              variant="outline"
                              size="xs"
                              onClick={() => {
                                setSelectedStudentUsnForPrediction(s.usn);
                                setIsTeacherPredictionModalOpen(true);
                              }}
                              title="Run AI Pass/Fail Forecast & What-If Simulator"
                              className="flex items-center gap-1 text-accent border-accent/40 hover:bg-accent/10 font-bold"
                            >
                              <Sparkles className="h-3.5 w-3.5 text-amber-500" /> Forecast
                            </Button>
                            <Button
                              variant="outline"
                              size="xs"
                              onClick={() => handleOpenEditMarks(s)}
                              title="Edit CIE Marks with Audit Trail"
                              className="flex items-center gap-1"
                            >
                              <Edit3 className="h-3.5 w-3.5" /> Marks
                            </Button>
                            <Button
                              variant="outline"
                              size="xs"
                              onClick={() => handleOpenHistory(s)}
                              title="Inspect Modification Audit Trail"
                            >
                              <History className="h-3.5 w-3.5" />
                            </Button>
                            <Button
                              variant="outline"
                              size="xs"
                              onClick={() => {
                                setRemarkStudent(s);
                                setRemarkText('');
                                setActionTaken('');
                              }}
                              title="Add Mentorship Guidance Remark"
                            >
                              <MessageSquare className="h-3.5 w-3.5" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan={6} className="py-6 text-center text-muted">
                      No student records match the active filter criteria.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Class Pass/Fail Analytics Tab */}
      {activeTab === 'pass_fail_analytics' && (
        <Card className="p-6">
          <CardHeader className="p-0 pb-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-accent animate-pulse" />
                  <CardTitle className="text-section">Class Pass/Fail Early Warning Intelligence</CardTitle>
                </div>
                <CardDescription>
                  XGBoost machine learning forecast for students enrolled in {selectedAssignment?.class_name || 'Class'} ({selectedAssignment?.subject_name || 'Subject'}).
                </CardDescription>
              </div>
              <Button
                variant="primary"
                onClick={() => {
                  setSelectedStudentUsnForPrediction(null);
                  setIsTeacherPredictionModalOpen(true);
                }}
                className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold flex items-center gap-2 shadow-md shrink-0"
              >
                <Sliders className="h-4 w-4" />
                Launch Pass/Fail Simulator
              </Button>
            </div>
          </CardHeader>

          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl border border-line bg-page p-4 dark:border-dark-line dark:bg-dark-page">
              <span className="text-xs font-semibold text-muted">Projected Class Pass Rate</span>
              <p className="mt-1 font-heading text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                {roster.length > 0 ? Math.round(((roster.length - (metrics.at_risk_count || 0)) / roster.length) * 100) : 95}%
              </p>
              <span className="text-[10px] text-muted">Based on current CIE & attendance figures</span>
            </div>

            <div className="rounded-xl border border-line bg-page p-4 dark:border-dark-line dark:bg-dark-page">
              <span className="text-xs font-semibold text-muted">Remedial Focus Cohort</span>
              <p className="mt-1 font-heading text-2xl font-bold text-rose-600">
                {metrics.at_risk_count || 0} students
              </p>
              <span className="text-[10px] text-muted">Predicted at-risk of course failure / backlogs</span>
            </div>

            <div className="rounded-xl border border-line bg-page p-4 dark:border-dark-line dark:bg-dark-page">
              <span className="text-xs font-semibold text-muted">Average Class CIE</span>
              <p className="mt-1 font-heading text-2xl font-bold text-accent">
                {metrics.average_cie || 35.0} / 50.0
              </p>
              <span className="text-[10px] text-muted">VTU Passing Qualifying bar: 20/50</span>
            </div>
          </div>

          <div className="mt-6">
            <h4 className="font-heading text-subheading font-bold text-ink dark:text-dark-text mb-3">
              Individual Student Forecast Roster
            </h4>
            <div className="overflow-x-auto rounded-card border border-line">
              <table className="w-full text-left text-caption">
                <thead className="border-b border-line bg-page text-muted uppercase text-[10px]">
                  <tr>
                    <th className="py-2.5 px-4">USN</th>
                    <th className="py-2.5 px-4">Student Name</th>
                    <th className="py-2.5 px-4 text-center">Total CIE</th>
                    <th className="py-2.5 px-4 text-center">Attendance</th>
                    <th className="py-2.5 px-4 text-center">Predicted Outcome</th>
                    <th className="py-2.5 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {roster.map((st) => (
                    <tr key={st.student_id} className="hover:bg-page/40">
                      <td className="py-2.5 px-4 font-mono font-semibold">{st.usn}</td>
                      <td className="py-2.5 px-4 font-medium">{st.name}</td>
                      <td className="py-2.5 px-4 text-center font-bold">{st.marks?.total_cie || 32}</td>
                      <td className="py-2.5 px-4 text-center">{st.attendance?.percentage || 85}%</td>
                      <td className="py-2.5 px-4 text-center">
                        <Pill variant={st.prediction?.risk_level === 'high' ? 'high' : 'low'}>
                          {st.prediction?.risk_level === 'high' ? 'AT-RISK / FAIL' : 'PASS'}
                        </Pill>
                      </td>
                      <td className="py-2.5 px-4 text-right">
                        <Button
                          variant="outline"
                          size="xs"
                          onClick={() => {
                            setSelectedStudentUsnForPrediction(st.usn);
                            setIsTeacherPredictionModalOpen(true);
                          }}
                          className="text-accent"
                        >
                          <Sparkles className="h-3 w-3 mr-1" /> Deep-Dive
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </Card>
      )}

      {/* 3. TAB: Bulk Matrix CIE Entry (Phase 10 Deep-Dive) */}
      {activeTab === 'bulk_cie' && (
        <Card className="p-6">
          <CardHeader className="p-0 pb-4">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <CardTitle className="text-section">
                    Bulk Matrix Continuous Internal Evaluation (CIE) Entry
                  </CardTitle>
                  <span className="rounded-pill bg-accent/10 px-2 py-0.5 text-xs font-mono font-bold text-accent">
                    VTU Top-2 Standard
                  </span>
                </div>
                <CardDescription className="mt-1">
                  Edit continuous assessment marks for all {roster.length} students simultaneously.
                  Formula: Best 2 CIE average + Assignment (10) + Quiz (10) = Total CIE (50). Passing is ≥ 20.0.
                </CardDescription>
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleDownloadMarksTemplate}
                  className="flex items-center gap-1.5"
                >
                  <FileDown className="h-4 w-4" />
                  <span>Download Marks CSV</span>
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleDownloadAttendanceTemplate}
                  className="flex items-center gap-1.5"
                >
                  <FileDown className="h-4 w-4" />
                  <span>Download Att. CSV</span>
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => setIsBulkSaveOpen(true)}
                  className="flex items-center gap-1.5 shadow-sm"
                >
                  <Save className="h-4 w-4" />
                  <span>Save All Changes</span>
                </Button>
              </div>
            </div>
          </CardHeader>

          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-caption border-collapse">
              <thead className="border-b border-line bg-page text-muted dark:border-dark-line dark:bg-dark-page">
                <tr>
                  <th className="py-3 px-3 font-semibold">USN</th>
                  <th className="py-3 px-3 font-semibold">Student Name</th>
                  <th className="py-3 px-2 font-semibold text-center w-24">CIE 1 (50)</th>
                  <th className="py-3 px-2 font-semibold text-center w-24">CIE 2 (50)</th>
                  <th className="py-3 px-2 font-semibold text-center w-24">CIE 3 (50)</th>
                  <th className="py-3 px-2 font-semibold text-center w-24">Assign (10)</th>
                  <th className="py-3 px-2 font-semibold text-center w-24">Quiz (10)</th>
                  <th className="py-3 px-3 font-semibold text-center w-28">Total CIE (50)</th>
                  <th className="py-3 px-3 font-semibold text-center w-28">VTU Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line dark:divide-dark-line">
                {roster.map((s) => {
                  const data = bulkMarksData[s.student_id] || {};
                  const liveTotal = parseFloat(data.total_cie) || 0;
                  const isPassing = liveTotal >= 20.0;

                  return (
                    <tr key={s.student_id} className="hover:bg-page/40 transition-colors">
                      <td className="py-2.5 px-3 font-mono font-bold text-ink dark:text-dark-text">
                        {s.usn}
                      </td>
                      <td className="py-2.5 px-3 font-medium text-ink dark:text-dark-text">
                        {s.name}
                      </td>
                      <td className="py-2.5 px-2 text-center">
                        <input
                          type="number"
                          step="0.5"
                          min="0"
                          max="50"
                          value={data.cie1 !== undefined ? data.cie1 : ''}
                          onChange={(e) => handleBulkMarksChange(s.student_id, 'cie1', e.target.value)}
                          className="w-20 rounded border border-line bg-page px-2 py-1 text-center font-mono text-caption focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-page dark:text-dark-text"
                        />
                      </td>
                      <td className="py-2.5 px-2 text-center">
                        <input
                          type="number"
                          step="0.5"
                          min="0"
                          max="50"
                          value={data.cie2 !== undefined ? data.cie2 : ''}
                          onChange={(e) => handleBulkMarksChange(s.student_id, 'cie2', e.target.value)}
                          className="w-20 rounded border border-line bg-page px-2 py-1 text-center font-mono text-caption focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-page dark:text-dark-text"
                        />
                      </td>
                      <td className="py-2.5 px-2 text-center">
                        <input
                          type="number"
                          step="0.5"
                          min="0"
                          max="50"
                          value={data.cie3 !== undefined ? data.cie3 : ''}
                          onChange={(e) => handleBulkMarksChange(s.student_id, 'cie3', e.target.value)}
                          className="w-20 rounded border border-line bg-page px-2 py-1 text-center font-mono text-caption focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-page dark:text-dark-text"
                        />
                      </td>
                      <td className="py-2.5 px-2 text-center">
                        <input
                          type="number"
                          step="0.5"
                          min="0"
                          max="10"
                          value={data.assignment_marks !== undefined ? data.assignment_marks : ''}
                          onChange={(e) => handleBulkMarksChange(s.student_id, 'assignment_marks', e.target.value)}
                          className="w-20 rounded border border-line bg-page px-2 py-1 text-center font-mono text-caption focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-page dark:text-dark-text"
                        />
                      </td>
                      <td className="py-2.5 px-2 text-center">
                        <input
                          type="number"
                          step="0.5"
                          min="0"
                          max="10"
                          value={data.quiz_marks !== undefined ? data.quiz_marks : ''}
                          onChange={(e) => handleBulkMarksChange(s.student_id, 'quiz_marks', e.target.value)}
                          className="w-20 rounded border border-line bg-page px-2 py-1 text-center font-mono text-caption focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-page dark:text-dark-text"
                        />
                      </td>
                      <td className="py-2.5 px-3 text-center">
                        <span className={`font-mono font-bold text-sm ${isPassing ? 'text-accent' : 'text-risk-high'}`}>
                          {liveTotal.toFixed(1)}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-center">
                        {isPassing ? (
                          <span className="inline-flex items-center gap-1 rounded bg-emerald-500/15 px-2 py-0.5 text-[10px] font-bold text-emerald-600 dark:text-emerald-400">
                            <Check className="h-3 w-3" /> PASSING
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 rounded bg-risk-high/15 px-2 py-0.5 text-[10px] font-bold text-risk-high">
                            <AlertTriangle className="h-3 w-3" /> REMEDIAL
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* 4. TAB: Log Session Attendance */}
      {activeTab === 'attendance_session' && (
        <Card className="p-6">
          <CardHeader className="p-0 pb-4">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <CardTitle className="text-section">Daily Lecture Session Attendance Logger</CardTitle>
                <CardDescription>
                  Record attendance for {selectedAssignment?.subject_name} ({selectedAssignment?.class_name})
                </CardDescription>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <input
                  type="date"
                  value={sessionDate}
                  onChange={(e) => setSessionDate(e.target.value)}
                  className="rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                />
                <Button variant="outline" size="sm" onClick={handleMarkAllPresent}>
                  All Present
                </Button>
                <Button variant="outline" size="sm" onClick={handleMarkAllAbsent}>
                  All Absent
                </Button>
                <Button variant="outline" size="sm" onClick={handleInvertAttendance}>
                  Invert
                </Button>
              </div>
            </div>

            {/* Quick Session Summary Banner */}
            <div className="mt-4 flex items-center justify-between rounded-lg bg-page p-3 border border-line dark:border-dark-line dark:bg-dark-page text-caption">
              <div className="flex items-center gap-4">
                <span>Present: <strong className="text-emerald-600">{totalPresentCount}</strong></span>
                <span>Absent: <strong className="text-risk-high">{totalAbsentCount}</strong></span>
                <span>Total: <strong>{roster.length}</strong></span>
              </div>
              <div>
                <span>Session Attendance: <strong className="text-accent">{Math.round((totalPresentCount / (roster.length || 1)) * 100)}%</strong></span>
              </div>
            </div>
          </CardHeader>

          {/* Student Toggle Grid */}
          <div className="mt-4 grid grid-cols-1 gap-2.5 sm:grid-cols-2 lg:grid-cols-3">
            {roster.map((s) => {
              const isPresent = sessionAttendance[s.student_id] !== false;
              return (
                <div
                  key={s.student_id}
                  onClick={() =>
                    setSessionAttendance((prev) => ({
                      ...prev,
                      [s.student_id]: !isPresent
                    }))
                  }
                  className={`flex cursor-pointer items-center justify-between rounded-input border p-3 transition-colors ${
                    isPresent
                      ? 'border-risk-low/40 bg-risk-low/10 dark:bg-risk-low/20'
                      : 'border-risk-high/40 bg-risk-high/10 dark:bg-risk-high/20'
                  }`}
                >
                  <div>
                    <strong className="font-heading text-caption font-bold text-ink dark:text-dark-text">
                      {s.name}
                    </strong>
                    <span className="font-mono text-xs text-muted block">{s.usn}</span>
                  </div>

                  <span
                    className={`flex items-center gap-1 rounded px-2.5 py-1 text-xs font-bold ${
                      isPresent ? 'bg-risk-low text-white' : 'bg-risk-high text-white'
                    }`}
                  >
                    {isPresent ? <UserCheck className="h-3.5 w-3.5" /> : <UserX className="h-3.5 w-3.5" />}
                    {isPresent ? 'Present' : 'Absent'}
                  </span>
                </div>
              );
            })}
          </div>

          <div className="mt-6 flex justify-end">
            <Button
              variant="primary"
              size="md"
              loading={submittingAttendance}
              onClick={handleSubmitAttendance}
              className="flex items-center gap-2"
            >
              <CheckCircle2 className="h-4 w-4" />
              Commit Session Attendance & Update Averages
            </Button>
          </div>
        </Card>
      )}

      {/* 5. TAB: Class Marks Audit Trail Inspector (Phase 10 Deep-Dive) */}
      {activeTab === 'audit_history' && (
        <Card className="p-6">
          <CardHeader className="p-0 pb-4">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <CardTitle className="text-section">
                  Marks Alteration Institutional Audit Trail
                </CardTitle>
                <CardDescription>
                  Chronological, tamper-evident log of every modification made to continuous assessment marks for this class.
                </CardDescription>
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={() => loadClassAuditHistory()}
                className="flex items-center gap-1.5"
              >
                <RefreshCw className={`h-4 w-4 ${loadingAuditHistory ? 'animate-spin' : ''}`} />
                <span>Refresh Log</span>
              </Button>
            </div>
          </CardHeader>

          {loadingAuditHistory ? (
            <div className="py-12 text-center text-muted">
              <RefreshCw className="mx-auto h-6 w-6 animate-spin text-accent" />
              <p className="mt-2 text-caption">Loading tamper-evident audit records...</p>
            </div>
          ) : classAuditHistory.length === 0 ? (
            <div className="py-12 text-center text-muted">
              <ShieldCheck className="mx-auto h-8 w-8 text-muted/60" />
              <p className="mt-2 text-caption">No marks alterations logged for this class yet. All entries are in original state.</p>
            </div>
          ) : (
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-left text-caption border-collapse">
                <thead className="border-b border-line bg-page text-muted dark:border-dark-line dark:bg-dark-page">
                  <tr>
                    <th className="py-3 px-3 font-semibold">Timestamp</th>
                    <th className="py-3 px-3 font-semibold">Student Name (USN)</th>
                    <th className="py-3 px-3 font-semibold">Assessment Component</th>
                    <th className="py-3 px-3 font-semibold text-center">Score Delta</th>
                    <th className="py-3 px-3 font-semibold">Altered By</th>
                    <th className="py-3 px-3 font-semibold">Audit Justification Reason</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line dark:divide-dark-line">
                  {classAuditHistory.map((item) => (
                    <tr key={item.history_id} className="hover:bg-page/40 transition-colors">
                      <td className="py-3 px-3 text-[11px] text-muted whitespace-nowrap">
                        {item.changed_at ? new Date(item.changed_at).toLocaleString() : 'N/A'}
                      </td>
                      <td className="py-3 px-3 font-medium text-ink dark:text-dark-text">
                        {item.student_name}
                        <span className="block font-mono text-xs text-muted">{item.usn}</span>
                      </td>
                      <td className="py-3 px-3 font-mono font-bold text-accent uppercase">
                        {item.field_name}
                      </td>
                      <td className="py-3 px-3 text-center">
                        <div className="inline-flex items-center gap-1.5 font-mono text-xs">
                          <span className="line-through text-muted">{item.old_value}</span>
                          <ChevronRight className="h-3 w-3 text-muted" />
                          <strong className="text-emerald-600 dark:text-emerald-400">{item.new_value}</strong>
                        </div>
                      </td>
                      <td className="py-3 px-3 text-muted">
                        <span className="font-semibold text-ink dark:text-dark-text">{item.changed_by}</span>
                        <span className="block text-[10px] uppercase text-muted">Role: {item.changed_by_role}</span>
                      </td>
                      <td className="py-3 px-3 italic text-xs text-ink dark:text-dark-text max-w-xs">
                        "{item.reason}"
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}

      {/* 6. TAB: Batch CSV Ingest */}
      {activeTab === 'batch_upload' && (
        <div className="space-y-6">
          <Card className="p-6">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="text-section">Batch CSV Data Ingestion</CardTitle>
              <CardDescription>
                Upload bulk student marks or session attendance using standardized institutional CSV templates.
              </CardDescription>
            </CardHeader>

            <form onSubmit={handleUploadCsv} className="space-y-4 pt-2">
              <div className="flex gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="upload_type"
                    value="marks"
                    checked={uploadType === 'marks'}
                    onChange={() => setUploadType('marks')}
                  />
                  <span className="text-caption font-semibold">Continuous Assessment Marks (CIE)</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="upload_type"
                    value="attendance"
                    checked={uploadType === 'attendance'}
                    onChange={() => setUploadType('attendance')}
                  />
                  <span className="text-caption font-semibold">Class Attendance Aggregates</span>
                </label>
              </div>

              {/* Template Format Note */}
              <div className="rounded-input border border-line bg-page p-3 text-caption text-muted dark:border-dark-line dark:bg-dark-page">
                <strong className="text-ink dark:text-dark-text">Expected CSV Column Headers:</strong>{' '}
                {uploadType === 'marks' ? (
                  <code className="font-mono text-accent">usn, cie1, cie2, cie3, assignment_marks, quiz_marks</code>
                ) : (
                  <code className="font-mono text-accent">usn, total_classes, attended_classes</code>
                )}
              </div>

              {/* File Input */}
              <div>
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => setCsvFile(e.target.files[0])}
                  className="w-full rounded-input border border-line bg-surface p-2 text-caption file:mr-4 file:rounded-input file:border-0 file:bg-accent file:px-3 file:py-1.5 file:text-caption file:font-semibold file:text-white hover:file:bg-accent-hover dark:border-dark-line dark:bg-dark-surface"
                />
              </div>

              <div className="flex justify-end gap-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={uploadType === 'marks' ? handleDownloadMarksTemplate : handleDownloadAttendanceTemplate}
                >
                  <FileDown className="h-4 w-4" /> Download Sample CSV
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  loading={uploadingCsv}
                  className="flex items-center gap-2"
                >
                  <Upload className="h-4 w-4" />
                  Process and Ingest CSV
                </Button>
              </div>
            </form>
          </Card>

          {/* Results Feedback */}
          {uploadResults && (
            <Card className="p-6">
              <CardTitle className="text-section flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-risk-low" />
                Upload Ingestion Summary
              </CardTitle>
              <p className="mt-1 text-caption text-muted">
                {uploadResults.processed_count} rows updated successfully. {uploadResults.error_count} errors encountered.
              </p>

              {uploadResults.errors?.length > 0 && (
                <div className="mt-4 space-y-1.5 rounded-input border border-risk-high/30 bg-risk-high/10 p-3 text-xs text-risk-high">
                  {uploadResults.errors.map((err, i) => (
                    <p key={i}>
                      Line {err.row}: {err.usn ? `[${err.usn}] ` : ''}{err.error}
                    </p>
                  ))}
                </div>
              )}
            </Card>
          )}
        </div>
      )}

      {/* 7. TAB: Broadcast Notice Dispatcher */}
      {activeTab === 'broadcast' && (
        <Card className="p-6">
          <CardHeader className="p-0 pb-4">
            <CardTitle className="text-section">Broadcast Academic Notices & Warning Bulletins</CardTitle>
            <CardDescription>
              Transmit official class instructions or warning circulars with automated parent forwarding.
            </CardDescription>
          </CardHeader>

          <form onSubmit={handleBroadcastNotice} className="space-y-4 pt-2">
            <div>
              <label className="block text-caption font-semibold text-ink dark:text-dark-text">
                Target Cohort
              </label>
              <div className="mt-1.5 flex gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="target"
                    value="all"
                    checked={broadcastTarget === 'all'}
                    onChange={() => setBroadcastTarget('all')}
                  />
                  <span className="text-caption font-medium">Entire Class ({roster.length} students)</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="target"
                    value="shortage"
                    checked={broadcastTarget === 'shortage'}
                    onChange={() => {
                      setBroadcastTarget('shortage');
                      setSelectedStudentIds(roster.filter((s) => s.attendance.is_shortage).map((s) => s.student_id));
                    }}
                  />
                  <span className="text-caption font-medium">
                    Attendance Shortage Cohort only ({roster.filter((s) => s.attendance.is_shortage).length} students)
                  </span>
                </label>
              </div>
            </div>

            <div>
              <label className="block text-caption font-semibold text-ink dark:text-dark-text">
                Notice Subject
              </label>
              <input
                type="text"
                value={broadcastSubject}
                onChange={(e) => setBroadcastSubject(e.target.value)}
                placeholder="e.g. CIE 2 Syllabus & Attendance Shortage Warning"
                className="mt-1.5 w-full rounded-input border border-line bg-surface px-3.5 py-2 text-caption text-ink placeholder:text-muted/60 focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
              />
            </div>

            <div>
              <label className="block text-caption font-semibold text-ink dark:text-dark-text">
                Notice Content
              </label>
              <textarea
                rows={5}
                value={broadcastMessage}
                onChange={(e) => setBroadcastMessage(e.target.value)}
                placeholder="Write notice instructions or warning details..."
                className="mt-1.5 w-full rounded-input border border-line bg-surface p-3.5 text-caption text-ink placeholder:text-muted/60 focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                required
              />
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="forwardParent"
                checked={forwardToParents}
                onChange={(e) => setForwardToParents(e.target.checked)}
                className="rounded text-accent focus:ring-accent"
              />
              <label htmlFor="forwardParent" className="text-caption font-medium text-ink dark:text-dark-text cursor-pointer">
                Automatically deliver copy to registered parent mobile in-app portal
              </label>
            </div>

            <div className="flex justify-end">
              <Button
                type="submit"
                variant="primary"
                loading={broadcasting}
                className="flex items-center gap-2"
              >
                <Send className="h-4 w-4" />
                Dispatch Notice to Cohort
              </Button>
            </div>
          </form>
        </Card>
      )}

      {/* 8. MODAL: Edit Marks (Single Student) with Mandatory Audit Trail */}
      {editingStudent && (
        <Modal
          isOpen={true}
          onClose={() => setEditingStudent(null)}
          title={`Edit CIE Marks: ${editingStudent.name} (${editingStudent.usn})`}
        >
          <form onSubmit={handleSaveMarks} className="space-y-4">
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block text-caption font-semibold text-muted">CIE 1 (50)</label>
                <input
                  type="number"
                  step="0.5"
                  max="50"
                  value={marksForm.cie1}
                  onChange={(e) => setMarksForm({ ...marksForm, cie1: e.target.value })}
                  className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                />
              </div>
              <div>
                <label className="block text-caption font-semibold text-muted">CIE 2 (50)</label>
                <input
                  type="number"
                  step="0.5"
                  max="50"
                  value={marksForm.cie2}
                  onChange={(e) => setMarksForm({ ...marksForm, cie2: e.target.value })}
                  className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                />
              </div>
              <div>
                <label className="block text-caption font-semibold text-muted">CIE 3 (50)</label>
                <input
                  type="number"
                  step="0.5"
                  max="50"
                  value={marksForm.cie3}
                  onChange={(e) => setMarksForm({ ...marksForm, cie3: e.target.value })}
                  className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                />
              </div>
              <div>
                <label className="block text-caption font-semibold text-muted">Assignment (10)</label>
                <input
                  type="number"
                  step="0.5"
                  max="10"
                  value={marksForm.assignment_marks}
                  onChange={(e) => setMarksForm({ ...marksForm, assignment_marks: e.target.value })}
                  className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                />
              </div>
              <div>
                <label className="block text-caption font-semibold text-muted">Quiz (10)</label>
                <input
                  type="number"
                  step="0.5"
                  max="10"
                  value={marksForm.quiz_marks}
                  onChange={(e) => setMarksForm({ ...marksForm, quiz_marks: e.target.value })}
                  className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                />
              </div>
            </div>

            {/* Mandatory Audit Trail Reason Input */}
            <div className="rounded-input border border-accent/30 bg-accent/5 p-3.5 dark:bg-accent/10">
              <label className="block text-caption font-bold text-accent">
                Reason for Marks Alteration (Mandatory Audit Trail Log) *
              </label>
              <textarea
                rows={2}
                value={marksForm.reason}
                onChange={(e) => setMarksForm({ ...marksForm, reason: e.target.value })}
                placeholder="Specify justification (e.g. Recheck application #VTU-402, Question 3 score re-evaluated)"
                className="mt-1.5 w-full rounded-input border border-line bg-surface p-2 text-caption text-ink dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                required
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" type="button" onClick={() => setEditingStudent(null)}>
                Cancel
              </Button>
              <Button variant="primary" type="submit" loading={updatingMarks}>
                Commit & Log Audit
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* 9. MODAL: Bulk Marks Save Confirmation with Mandatory Audit Reason */}
      {isBulkSaveOpen && (
        <Modal
          isOpen={true}
          onClose={() => setIsBulkSaveOpen(false)}
          title={`Commit Bulk Marks: ${selectedAssignment?.class_name} - ${selectedAssignment?.subject_name}`}
        >
          <form onSubmit={handleSaveBulkMarks} className="space-y-4">
            <p className="text-caption text-muted dark:text-dark-muted">
              You are committing continuous evaluation scores across <strong>{roster.length} students</strong>.
              VTU best-of-2 continuous internal evaluation totals will be recalculated and recorded in the tamper-evident audit ledger.
            </p>

            <div className="rounded-input border border-accent/30 bg-accent/5 p-3.5 dark:bg-accent/10">
              <label className="block text-caption font-bold text-accent">
                Official Institutional Justification Reason *
              </label>
              <textarea
                rows={3}
                value={bulkSaveReason}
                onChange={(e) => setBulkSaveReason(e.target.value)}
                placeholder="e.g. Phase 10 Continuous Internal Assessment (CIE-1) official faculty mark submission."
                className="mt-1.5 w-full rounded-input border border-line bg-surface p-2.5 text-caption text-ink dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                required
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" type="button" onClick={() => setIsBulkSaveOpen(false)}>
                Cancel
              </Button>
              <Button variant="primary" type="submit" loading={savingBulkMarks}>
                Commit All & Record Audit Trail
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* 10. MODAL: Adjust Individual Attendance Record */}
      {editingAttendanceStudent && (
        <Modal
          isOpen={true}
          onClose={() => setEditingAttendanceStudent(null)}
          title={`Adjust Attendance: ${editingAttendanceStudent.name} (${editingAttendanceStudent.usn})`}
        >
          <form onSubmit={handleSaveAttendance} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-caption font-semibold text-muted">Total Classes Held *</label>
                <input
                  type="number"
                  min="1"
                  value={attendanceForm.total_classes}
                  onChange={(e) => setAttendanceForm({ ...attendanceForm, total_classes: e.target.value })}
                  className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                  required
                />
              </div>
              <div>
                <label className="block text-caption font-semibold text-muted">Classes Attended *</label>
                <input
                  type="number"
                  min="0"
                  max={attendanceForm.total_classes}
                  value={attendanceForm.attended_classes}
                  onChange={(e) => setAttendanceForm({ ...attendanceForm, attended_classes: e.target.value })}
                  className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                  required
                />
              </div>
            </div>

            <div className="rounded-input border border-accent/30 bg-accent/5 p-3.5 dark:bg-accent/10">
              <label className="block text-caption font-bold text-accent">
                Reason for Attendance Override / Condonation *
              </label>
              <textarea
                rows={2}
                value={attendanceForm.reason}
                onChange={(e) => setAttendanceForm({ ...attendanceForm, reason: e.target.value })}
                placeholder="e.g. Medical certificate #VTU-MED-89 approved by HoD, or VTU University Sports representational duty."
                className="mt-1.5 w-full rounded-input border border-line bg-surface p-2 text-caption text-ink dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                required
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" type="button" onClick={() => setEditingAttendanceStudent(null)}>
                Cancel
              </Button>
              <Button variant="primary" type="submit" loading={updatingAttendance}>
                Save & Update Attendance
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* 11. MODAL: View Audit History */}
      {historyStudent && (
        <Modal
          isOpen={true}
          onClose={() => setHistoryStudent(null)}
          title={`Marks Audit Trail: ${historyStudent.name} (${historyStudent.usn})`}
        >
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {historyLoading ? (
              <p className="text-center text-caption text-muted py-4">Loading audit logs...</p>
            ) : marksHistory.length > 0 ? (
              marksHistory.map((h) => (
                <div key={h.id} className="rounded-input border border-line bg-page p-3 text-caption dark:border-dark-line dark:bg-dark-page">
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-semibold text-accent uppercase">{h.field_name}</span>
                    <span className="text-[11px] text-muted">{new Date(h.changed_at).toLocaleString()}</span>
                  </div>
                  <div className="mt-1 flex items-center gap-2 text-xs">
                    <span className="line-through text-muted">{h.old_value}</span>
                    <ChevronRight className="h-3 w-3 text-muted" />
                    <strong className="text-risk-low">{h.new_value}</strong>
                    <span className="text-muted ml-auto">By: {h.editor_name || 'Faculty'}</span>
                  </div>
                  <p className="mt-1.5 text-xs text-ink dark:text-dark-text italic">
                    Reason: "{h.reason}"
                  </p>
                </div>
              ))
            ) : (
              <p className="text-center text-caption text-muted py-6">No historical modifications recorded for this entry.</p>
            )}
          </div>
        </Modal>
      )}

      {/* 12. MODAL: Add Mentorship Remark */}
      {remarkStudent && (
        <Modal
          isOpen={true}
          onClose={() => setRemarkStudent(null)}
          title={`Record Mentorship Remark: ${remarkStudent.name}`}
        >
          <form onSubmit={handleSaveRemark} className="space-y-4">
            <div>
              <label className="block text-caption font-semibold text-muted">Feedback / Observation *</label>
              <textarea
                rows={3}
                value={remarkText}
                onChange={(e) => setRemarkText(e.target.value)}
                placeholder="Enter academic observation or feedback for the student and parent..."
                className="mt-1 w-full rounded-input border border-line bg-surface p-2.5 text-caption text-ink dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                required
              />
            </div>

            <div>
              <label className="block text-caption font-semibold text-muted">Action Taken / Recommended Follow-up</label>
              <input
                type="text"
                value={actionTaken}
                onChange={(e) => setActionTaken(e.target.value)}
                placeholder="e.g. Referred to remedial tutorial, parent contacted regarding attendance"
                className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" type="button" onClick={() => setRemarkStudent(null)}>
                Cancel
              </Button>
              <Button variant="primary" type="submit" loading={savingRemark}>
                Save Remark
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* Teacher Pass/Fail Prediction Intelligence Modal */}
      <PassFailPredictionModal
        isOpen={isTeacherPredictionModalOpen}
        onClose={() => setIsTeacherPredictionModalOpen(false)}
        initialUsn={selectedStudentUsnForPrediction}
        title={selectedStudentUsnForPrediction ? `AI Exam Prediction: ${selectedStudentUsnForPrediction}` : "Class Examination Pass/Fail Intelligence"}
      />
    </div>
  );
}
