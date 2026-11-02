import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  ArrowLeft,
  User,
  Phone,
  Mail,
  GraduationCap,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  Download,
  MessageSquare,
  Send,
  BookOpen,
  Award,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Pill } from '@/components/ui/Pill';
import { RiskGauge } from '@/components/charts/RiskGauge';
import { ShapBars } from '@/components/charts/ShapBars';
import { AttendanceBar } from '@/components/charts/AttendanceBar';
import { SgpaTrend } from '@/components/charts/SgpaTrend';
import { STUDENTS, INITIAL_REMARKS } from '@/mocks/data';
import { formatDate } from '@/utils/format';
import { useAuth } from '@/context/AuthContext';

export default function StudentProfile() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { currentUser } = useAuth();

  // Find student by ID or USN
  const student =
    STUDENTS.find((s) => String(s.id) === String(id) || s.usn === id) || STUDENTS[0];

  // Remarks state
  const [remarks, setRemarks] = useState(() => {
    return INITIAL_REMARKS.filter((r) => r.studentId === student.id);
  });
  const [newRemarkText, setNewRemarkText] = useState('');
  const [isSubmittingRemark, setIsSubmittingRemark] = useState(false);
  const [hasContactedParent, setHasContactedParent] = useState(false);

  // Add new remark handler
  const handleSaveRemark = (e) => {
    e.preventDefault();
    if (!newRemarkText.trim()) {
      toast.error('Please enter a remark note.');
      return;
    }

    setIsSubmittingRemark(true);
    setTimeout(() => {
      const addedRemark = {
        id: Date.now(),
        studentId: student.id,
        authorName: currentUser?.name || 'Prof. Anita Rao',
        text: newRemarkText.trim(),
        createdAt: new Date().toISOString(),
      };
      setRemarks([addedRemark, ...remarks]);
      setNewRemarkText('');
      setIsSubmittingRemark(false);
      toast.success('Mentor remark saved and added to intervention log.');
    }, 400);
  };

  // Mark parent contacted
  const handleMarkContacted = () => {
    setHasContactedParent(true);
    toast.success(`Parent (${student.parentName}) recorded as contacted by phone/in-person.`);
  };

  return (
    <div className="space-y-6">
      {/* Back button & top bar */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <button
          onClick={() => navigate('/students')}
          className="inline-flex items-center gap-1.5 text-caption font-semibold text-muted hover:text-ink dark:text-dark-muted dark:hover:text-dark-text transition"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to student directory</span>
        </button>

        <div className="flex items-center gap-2">
          <Button
            variant={hasContactedParent ? 'outline' : 'primary'}
            size="sm"
            onClick={handleMarkContacted}
          >
            <CheckCircle2 className="h-3.5 w-3.5" />
            <span>{hasContactedParent ? 'Parent Contacted' : 'Mark Parent Contacted'}</span>
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() =>
              toast.success(`Exporting comprehensive dossier for ${student.name} (PDF)...`)
            }
          >
            <Download className="h-3.5 w-3.5" />
            <span>Export Dossier</span>
          </Button>
        </div>
      </div>

      {/* Student Profile Identity Header Card */}
      <Card className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex flex-col sm:flex-row sm:items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-card bg-accent font-heading text-2xl font-bold text-white shadow-subtle">
            {student.name.charAt(0)}
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="font-heading text-display font-bold text-ink dark:text-dark-text">
                {student.name}
              </h1>
              <Pill level={student.riskLevel} />
              <span className="font-mono text-caption text-muted dark:text-dark-muted">
                {student.usn}
              </span>
            </div>
            <p className="mt-1 text-caption text-muted dark:text-dark-muted">
              5th Semester CSE &bull; Section {student.section} &bull; PESITM Shivamogga &bull; Academic Year 2024-25
            </p>
          </div>
        </div>

        {/* Contact & Mentor Info Grid */}
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 rounded-input border border-line bg-page/40 p-3 text-caption dark:border-dark-line dark:bg-dark-surface/40">
          <div>
            <span className="text-muted dark:text-dark-muted">Assigned Mentor:</span>
            <p className="font-semibold text-ink dark:text-dark-text">{student.mentorName || 'Prof. Anita Rao'}</p>
          </div>
          <div>
            <span className="text-muted dark:text-dark-muted">Parent / Guardian:</span>
            <p className="font-semibold text-ink dark:text-dark-text">{student.parentName}</p>
          </div>
          <div>
            <span className="text-muted dark:text-dark-muted">Emergency Contact:</span>
            <p className="font-semibold text-ink dark:text-dark-text">{student.phone}</p>
          </div>
        </div>
      </Card>

      {/* Main 2-Column Layout */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left 2 Columns: Visual Analytics, Risk Gauge, SHAP, Attendance, GPA */}
        <div className="space-y-6 lg:col-span-2">
          {/* Risk Gauge Card */}
          <Card>
            <CardHeader>
              <div>
                <CardTitle>ML Predicted Risk & Early Diagnostic</CardTitle>
                <CardDescription>
                  Evaluated via XGBoost pipeline trained with SMOTE class balance and quantile transformations.
                </CardDescription>
              </div>
            </CardHeader>
            <div className="py-2">
              <RiskGauge score={student.riskScore} size={220} />
            </div>
          </Card>

          {/* TreeSHAP Local Feature Attribution Card */}
          <Card>
            <CardHeader>
              <div>
                <div className="flex items-center gap-2">
                  <CardTitle>Explainable AI (TreeSHAP Attributions)</CardTitle>
                  <span className="rounded-pill bg-accent/10 px-2 py-0.5 text-[10px] font-semibold text-accent">
                    Local Explanation
                  </span>
                </div>
                <CardDescription>
                  Diverging attributions indicating why the XGBoost model assigned this risk level. Red bars push risk upwards; green bars act as protective factors.
                </CardDescription>
              </div>
            </CardHeader>
            <ShapBars explanations={student.explanations} studentName={student.name} />
          </Card>

          {/* Subject Attendance Breakdown */}
          <Card>
            <CardHeader>
              <div>
                <div className="flex items-center gap-2">
                  <CardTitle>Subject-wise Attendance Compliance</CardTitle>
                  <span className="rounded-pill bg-risk-high/10 px-2 py-0.5 text-[10px] font-semibold text-risk-high">
                    75% VTU Threshold
                  </span>
                </div>
                <CardDescription>
                  Cumulative attendance logged across 5th Semester VTU courses.
                </CardDescription>
              </div>
            </CardHeader>
            <AttendanceBar subjects={student.subjectAttendance} height={240} />
          </Card>

          {/* SGPA Semester Progression */}
          <Card>
            <CardHeader>
              <div>
                <CardTitle>Historical Semester Performance (SGPA)</CardTitle>
                <CardDescription>
                  Grade trajectory from 1st to 5th Semester.
                </CardDescription>
              </div>
            </CardHeader>
            <div className="pt-2">
              <SgpaTrend
                history={student.sgpaHistory || [7.0, 7.2, 7.1, 7.3, 7.4]}
                targetGpa={7.0}
                height={220}
              />
            </div>
          </Card>
        </div>

        {/* Right 1 Column: Prescriptions & Mentor Intervention Timeline */}
        <div className="space-y-6">
          {/* Prescriptive Advisory Plan */}
          <Card>
            <CardHeader>
              <div>
                <div className="flex items-center gap-1.5">
                  <Award className="h-4 w-4 text-accent" />
                  <CardTitle>Recommended Action Plan</CardTitle>
                </div>
                <CardDescription>
                  Automated prescriptive guidance tailored to this student&apos;s risk profile.
                </CardDescription>
              </div>
            </CardHeader>

            <ul className="space-y-2.5">
              {(student.actions || [
                'Schedule bi-weekly counseling with assigned mentor.',
                'Attend Saturday remedial tutorial sessions for Theory of Computation.',
                'Submit revised CIE improvement assignment before next assessment.',
              ]).map((action, idx) => (
                <li
                  key={idx}
                  className="flex items-start gap-2.5 rounded-input border border-line bg-page/30 p-3 text-caption text-ink dark:border-dark-line dark:bg-dark-surface/40 dark:text-dark-text"
                >
                  <span className="mt-0.5 flex h-4 w-4 flex-shrink-0 items-center justify-center rounded-full bg-accent text-[10px] font-bold text-white">
                    {idx + 1}
                  </span>
                  <span>{action}</span>
                </li>
              ))}
            </ul>
          </Card>

          {/* Mentor Remarks & Intervention Log */}
          <Card>
            <CardHeader>
              <div>
                <div className="flex items-center gap-1.5">
                  <MessageSquare className="h-4 w-4 text-accent" />
                  <CardTitle>Mentor Remarks & Log</CardTitle>
                </div>
                <CardDescription>
                  Confidential advisory notes recorded by faculty counselors.
                </CardDescription>
              </div>
            </CardHeader>

            {/* Add New Remark Form */}
            <form onSubmit={handleSaveRemark} className="space-y-3 pb-4 border-b border-line dark:border-dark-line">
              <textarea
                rows={3}
                placeholder="Log observation notes, intervention actions, or parent counseling details..."
                value={newRemarkText}
                onChange={(e) => setNewRemarkText(e.target.value)}
                className="w-full rounded-input border border-line bg-surface p-2.5 text-body text-ink transition focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
              />
              <div className="flex justify-end">
                <Button
                  variant="primary"
                  size="sm"
                  type="submit"
                  isLoading={isSubmittingRemark}
                >
                  <Send className="h-3 w-3" />
                  <span>Save Remark</span>
                </Button>
              </div>
            </form>

            {/* Remarks Timeline */}
            <div className="mt-4 space-y-3 max-h-96 overflow-y-auto pr-1">
              {remarks.length === 0 ? (
                <p className="text-center text-caption text-muted py-4">
                  No mentor remarks logged yet for this student.
                </p>
              ) : (
                remarks.map((r) => (
                  <div
                    key={r.id}
                    className="rounded-input border border-line bg-page/30 p-3 text-caption dark:border-dark-line dark:bg-dark-surface/30"
                  >
                    <div className="flex items-center justify-between font-semibold text-ink dark:text-dark-text">
                      <span>{r.authorName}</span>
                      <span className="text-[10px] text-muted">{formatDate(r.createdAt)}</span>
                    </div>
                    <p className="mt-1 text-muted dark:text-dark-muted leading-relaxed">{r.text}</p>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
