import React, { useState } from 'react';
import toast from 'react-hot-toast';
import {
  GraduationCap,
  TrendingUp,
  Clock,
  BookOpen,
  Award,
  AlertCircle,
  CheckCircle2,
  Phone,
  Mail,
  User,
  Sparkles,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Pill } from '@/components/ui/Pill';
import { RiskGauge } from '@/components/charts/RiskGauge';
import { AttendanceBar } from '@/components/charts/AttendanceBar';
import { SgpaTrend } from '@/components/charts/SgpaTrend';
import { STUDENTS } from '@/mocks/data';
import { formatGpa } from '@/utils/format';

export default function MyProgress() {
  // Allow toggling between Poorvi (high performer) and Rohan (needs support) for demo
  const [selectedStudentId, setSelectedStudentId] = useState(1);

  const student =
    STUDENTS.find((s) => s.id === selectedStudentId) || STUDENTS[0];

  const isAtRisk = student.riskLevel === 'high';
  const latestGpa =
    student.sgpaHistory?.[student.sgpaHistory.length - 1] || 8.5;
  const predictedNextGpa = isAtRisk ? (latestGpa - 0.25).toFixed(2) : (latestGpa + 0.15).toFixed(2);

  return (
    <div className="space-y-6">
      {/* Top Banner & Quick Persona Switcher for Viva Demo */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-input bg-accent/10 text-accent">
              <GraduationCap className="h-4 w-4" />
            </span>
            <h1 className="font-heading text-display font-bold text-ink dark:text-dark-text">
              Your Academic Trajectory & Forecast
            </h1>
          </div>
          <p className="mt-1 text-body text-muted dark:text-dark-muted">
            PESITM Shivamogga &bull; Personalized learning analytics, ML risk assessment, and mentor guidance.
          </p>
        </div>

        {/* Demo Selector */}
        <div className="flex items-center gap-2 rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface">
          <span className="text-muted dark:text-dark-muted font-medium">Viewing as:</span>
          <select
            value={selectedStudentId}
            onChange={(e) => {
              setSelectedStudentId(Number(e.target.value));
              toast.success(`Switched view to student profile.`);
            }}
            className="bg-transparent font-semibold text-accent focus:outline-none cursor-pointer"
          >
            <option value={1}>Poorvi V S (Low Risk / 9.15 SGPA)</option>
            <option value={2}>Rohan Verma (High Risk / 5.20 SGPA)</option>
          </select>
        </div>
      </div>

      {/* Student Welcome Banner Card */}
      <Card className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-l-4 border-l-accent">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="font-heading text-heading font-bold text-ink dark:text-dark-text">
              Welcome back, {student.name}
            </h2>
            <Pill level={student.riskLevel} />
          </div>
          <p className="mt-1 text-caption text-muted dark:text-dark-muted">
            USN: <span className="font-mono font-semibold text-ink dark:text-dark-text">{student.usn}</span> &bull; 5th Semester Computer Science & Engineering &bull; Section {student.section}
          </p>
        </div>

        <div className="flex items-center gap-3 text-caption">
          <div className="rounded-input border border-line bg-page px-3 py-1.5 dark:border-dark-line dark:bg-dark-page">
            <span className="text-muted dark:text-dark-muted">Assigned Mentor: </span>
            <span className="font-semibold text-ink dark:text-dark-text">{student.mentorName || 'Prof. Anita Rao'}</span>
          </div>
        </div>
      </Card>

      {/* 4 Personal Metric Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="flex items-center gap-4">
          <div
            className={`flex h-12 w-12 items-center justify-center rounded-input ${
              student.attendance >= 75
                ? 'bg-risk-low/10 text-risk-low'
                : 'bg-risk-high/10 text-risk-high'
            }`}
          >
            <Clock className="h-6 w-6" />
          </div>
          <div>
            <p className="text-caption font-medium text-muted dark:text-dark-muted">Overall Attendance</p>
            <p className="font-heading text-heading font-bold text-ink dark:text-dark-text">
              {student.attendance}%
            </p>
            <p
              className={`text-[11px] font-semibold ${
                student.attendance >= 75 ? 'text-risk-low' : 'text-risk-high'
              }`}
            >
              {student.attendance >= 75
                ? 'Eligible for VTU Exam Hall Ticket'
                : 'Attendance Shortage (<75%)'}
            </p>
          </div>
        </Card>

        <Card className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-input bg-accent/10 text-accent">
            <BookOpen className="h-6 w-6" />
          </div>
          <div>
            <p className="text-caption font-medium text-muted dark:text-dark-muted">Internal Marks (CIE)</p>
            <p className="font-heading text-heading font-bold text-ink dark:text-dark-text">
              {student.internalMarks} / 50
            </p>
            <p className="text-[11px] text-muted">Continuous Internal Evaluation</p>
          </div>
        </Card>

        <Card className="flex items-center gap-4">
          <div
            className={`flex h-12 w-12 items-center justify-center rounded-input ${
              student.backlogs === 0
                ? 'bg-risk-low/10 text-risk-low'
                : 'bg-risk-high/10 text-risk-high'
            }`}
          >
            <AlertCircle className="h-6 w-6" />
          </div>
          <div>
            <p className="text-caption font-medium text-muted dark:text-dark-muted">Active Backlogs</p>
            <p
              className={`font-heading text-heading font-bold ${
                student.backlogs === 0 ? 'text-ink dark:text-dark-text' : 'text-risk-high'
              }`}
            >
              {student.backlogs} {student.backlogs === 1 ? 'Course' : 'Courses'}
            </p>
            <p className="text-[11px] text-muted">Uncleared VTU semester arrears</p>
          </div>
        </Card>

        <Card className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-input bg-accent/10 text-accent">
            <TrendingUp className="h-6 w-6" />
          </div>
          <div>
            <p className="text-caption font-medium text-muted dark:text-dark-muted">Predicted 6th Sem SGPA</p>
            <p className="font-heading text-heading font-bold text-accent">
              ~{predictedNextGpa} / 10.0
            </p>
            <p className="text-[11px] text-muted">Random Forest Regressor R&sup2; 0.966</p>
          </div>
        </Card>
      </div>

      {/* 2-Column Section: Left Gauge & Subject Attendance, Right GPA & Advice */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Risk Probability Gauge */}
        <Card>
          <CardHeader>
            <div>
              <CardTitle>Academic Standing & Dropout Risk</CardTitle>
              <CardDescription>
                Calculated using XGBoost classification based on current attendance and assessment marks.
              </CardDescription>
            </div>
          </CardHeader>
          <div className="py-2">
            <RiskGauge score={student.riskScore} size={220} />
          </div>
        </Card>

        {/* Semester GPA Trend */}
        <Card>
          <CardHeader>
            <div>
              <CardTitle>Your Semester-by-Semester Progression</CardTitle>
              <CardDescription>
                SGPA from 1st to 5th semester compared against VTU First Class distinction (7.0).
              </CardDescription>
            </div>
          </CardHeader>
          <div className="h-64 pt-2">
            <SgpaTrend
              history={student.sgpaHistory || [7.0, 7.2, 7.1, 7.3, 7.4]}
              targetGpa={7.0}
              height={230}
            />
          </div>
        </Card>
      </div>

      {/* Subject Attendance Breakdown & Recommended Actions */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <div>
              <div className="flex items-center gap-2">
                <CardTitle>Subject-wise Attendance Status</CardTitle>
                <span className="rounded-pill bg-risk-high/10 px-2 py-0.5 text-[10px] font-semibold text-risk-high">
                  75% Requirement
                </span>
              </div>
              <CardDescription>
                Make sure you attend all scheduled classes to stay above the 75% eligibility mark.
              </CardDescription>
            </div>
          </CardHeader>
          <AttendanceBar subjects={student.subjectAttendance} height={230} />
        </Card>

        {/* Personalized Improvement Suggestions */}
        <Card>
          <CardHeader>
            <div>
              <div className="flex items-center gap-1.5">
                <Award className="h-4 w-4 text-accent" />
                <CardTitle>Personalized Improvement Plan</CardTitle>
              </div>
              <CardDescription>
                Actionable steps generated by the system to maximize your semester grade.
              </CardDescription>
            </div>
          </CardHeader>

          <div className="space-y-3">
            {(student.actions || [
              'Continue maintaining above 90% attendance across all subjects.',
              'Prepare for university lab viva and internal project submission.',
            ]).map((action, idx) => (
              <div
                key={idx}
                className="flex items-start gap-3 rounded-input border border-line bg-page/40 p-3 text-caption dark:border-dark-line dark:bg-dark-surface/40"
              >
                <span className="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-accent text-[11px] font-bold text-white">
                  {idx + 1}
                </span>
                <p className="text-ink dark:text-dark-text font-medium leading-relaxed">{action}</p>
              </div>
            ))}
          </div>

          <div className="mt-4 rounded-input border border-line bg-accent/5 p-3 text-caption text-ink dark:border-dark-line dark:bg-accent/10 dark:text-dark-text">
            <span className="font-semibold text-accent">Need Mentorship Assistance? </span>
            <span>
              Contact your faculty counselor <b>{student.mentorName || 'Prof. Anita Rao'}</b> in Room CS-204 or via email.
            </span>
          </div>
        </Card>
      </div>
    </div>
  );
}
