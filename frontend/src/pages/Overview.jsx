import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  Users,
  AlertTriangle,
  GraduationCap,
  Calendar,
  Filter,
  Download,
  ArrowRight,
  TrendingUp,
  Clock,
  Sparkles,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Pill } from '@/components/ui/Pill';
import { RiskStrip } from '@/components/charts/RiskStrip';
import { RiskDonut } from '@/components/charts/RiskDonut';
import { SgpaTrend } from '@/components/charts/SgpaTrend';
import { STUDENTS, CLASSES } from '@/mocks/data';
import { formatPercentage, formatGpa } from '@/utils/format';

export default function Overview() {
  const navigate = useNavigate();
  const [selectedSection, setSelectedSection] = useState('ALL');

  // Filter students by selected section
  const filteredStudents =
    selectedSection === 'ALL'
      ? STUDENTS
      : STUDENTS.filter((s) => s.section === selectedSection);

  // Compute metrics
  const totalStudents = filteredStudents.length;
  const highRiskStudents = filteredStudents.filter((s) => s.riskLevel === 'high');
  const mediumRiskStudents = filteredStudents.filter((s) => s.riskLevel === 'medium');
  const lowRiskStudents = filteredStudents.filter((s) => s.riskLevel === 'low');

  const avgAttendance =
    filteredStudents.reduce((acc, s) => acc + (s.attendance || 0), 0) / (totalStudents || 1);

  const avgGpa =
    filteredStudents.reduce(
      (acc, s) => acc + (s.sgpaHistory?.[s.sgpaHistory.length - 1] || 7.0),
      0
    ) / (totalStudents || 1);

  // Top at-risk students needing immediate attention
  const criticalStudents = [...highRiskStudents].sort(
    (a, b) => (b.riskScore || 0) - (a.riskScore || 0)
  );

  return (
    <div className="space-y-6">
      {/* Top Banner & Filters */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="font-heading text-display font-bold text-ink dark:text-dark-text">
            Academic Monitoring & Early Intervention
          </h1>
          <p className="mt-1 text-body text-muted dark:text-dark-muted">
            PESITM Shivamogga &bull; 5th Semester Computer Science and Engineering cohort analytics.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Section Filter */}
          <div className="flex items-center gap-1.5 rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface">
            <Filter className="h-3.5 w-3.5 text-muted" />
            <span className="font-semibold text-muted dark:text-dark-muted">Section:</span>
            <select
              value={selectedSection}
              onChange={(e) => setSelectedSection(e.target.value)}
              className="bg-transparent font-semibold text-ink dark:text-dark-text focus:outline-none cursor-pointer"
            >
              <option value="ALL">All Sections (60)</option>
              <option value="A">Section A (32)</option>
              <option value="B">Section B (28)</option>
            </select>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={() => toast.success('Exporting VTU Class Analytics summary (PDF)...')}
          >
            <Download className="h-3.5 w-3.5" />
            <span>Export Report</span>
          </Button>
        </div>
      </div>

      {/* 4 Summary Stat Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-input bg-accent/10 text-accent">
            <Users className="h-6 w-6" />
          </div>
          <div>
            <p className="text-caption font-medium text-muted dark:text-dark-muted">Enrolled Cohort</p>
            <p className="font-heading text-heading font-bold text-ink dark:text-dark-text">
              {totalStudents} Students
            </p>
            <p className="text-[11px] text-muted">5th Sem CSE &bull; VTU 2021 Scheme</p>
          </div>
        </Card>

        <Card className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-input bg-risk-high/10 text-risk-high">
            <AlertTriangle className="h-6 w-6" />
          </div>
          <div>
            <p className="text-caption font-medium text-muted dark:text-dark-muted">Requires Intervention</p>
            <p className="font-heading text-heading font-bold text-risk-high">
              {highRiskStudents.length} Students
            </p>
            <p className="text-[11px] font-semibold text-risk-high">
              {Math.round((highRiskStudents.length / totalStudents) * 100)}% of cohort &bull; High Risk
            </p>
          </div>
        </Card>

        <Card className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-input bg-risk-low/10 text-risk-low">
            <Clock className="h-6 w-6" />
          </div>
          <div>
            <p className="text-caption font-medium text-muted dark:text-dark-muted">Average Attendance</p>
            <p className="font-heading text-heading font-bold text-ink dark:text-dark-text">
              {avgAttendance.toFixed(1)}%
            </p>
            <p className="text-[11px] text-risk-low font-medium">
              &gt; 75% Regulatory Requirement
            </p>
          </div>
        </Card>

        <Card className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-input bg-accent/10 text-accent">
            <TrendingUp className="h-6 w-6" />
          </div>
          <div>
            <p className="text-caption font-medium text-muted dark:text-dark-muted">Cohort Mean SGPA</p>
            <p className="font-heading text-heading font-bold text-ink dark:text-dark-text">
              {avgGpa.toFixed(2)} / 10.0
            </p>
            <p className="text-[11px] text-muted">VTU First Class Average</p>
          </div>
        </Card>
      </div>

      {/* Signature Risk Strip Card */}
      <Card>
        <CardHeader>
          <div>
            <div className="flex items-center gap-2">
              <CardTitle>Cohort Risk Distribution Spectrum</CardTitle>
              <span className="rounded-pill bg-accent/10 px-2 py-0.5 text-[10px] font-semibold text-accent">
                TreeSHAP Sorted
              </span>
            </div>
            <CardDescription>
              Every thin bar represents a student sorted from lowest risk to critical attention. Hover for details or click to open student profile.
            </CardDescription>
          </div>
        </CardHeader>

        <div className="pt-2">
          <RiskStrip
            students={filteredStudents}
            onSelectStudent={(s) => navigate(`/students/${s.id}`)}
          />
        </div>
      </Card>

      {/* Two-Column Visual Analytics: Risk Donut + SGPA Trend */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>Predictive Risk Stratification</CardTitle>
              <CardDescription>
                Categorization evaluated by XGBoost ML Model (Thresholds: &lt;35% Safe, 35-60% Moderate, &ge;60% Critical).
              </CardDescription>
            </div>
          </CardHeader>
          <div className="h-64">
            <RiskDonut students={filteredStudents} />
          </div>
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>Cohort Academic Progression (SGPA Trend)</CardTitle>
              <CardDescription>
                Mean semester grade trajectory across Semesters 1 through 5 with VTU 7.0 benchmark line.
              </CardDescription>
            </div>
          </CardHeader>
          <div className="h-64 pt-2">
            <SgpaTrend
              history={[7.15, 7.28, 7.35, 7.42, 7.56]}
              targetGpa={7.0}
              height={230}
            />
          </div>
        </Card>
      </div>

      {/* Priority Attention Table: Top At-Risk Students */}
      <Card>
        <CardHeader>
          <div>
            <div className="flex items-center gap-2">
              <CardTitle>Students Requiring Immediate Faculty Intervention</CardTitle>
              <span className="rounded-pill bg-risk-high/10 px-2.5 py-0.5 text-[11px] font-semibold text-risk-high border border-risk-high/30">
                Action Required ({highRiskStudents.length})
              </span>
            </div>
            <CardDescription>
              Students with predicted risk &ge; 60% due to attendance shortages (&lt;75%) or multiple backlog arrears.
            </CardDescription>
          </div>

          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/students')}
          >
            <span>View All Students</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Button>
        </CardHeader>

        <div className="overflow-x-auto rounded-input border border-line dark:border-dark-line">
          <table className="w-full text-left text-body">
            <thead className="border-b border-line bg-page/60 text-caption font-semibold uppercase text-muted dark:border-dark-line dark:bg-dark-page/60 dark:text-dark-muted">
              <tr>
                <th className="px-4 py-3">Student Name</th>
                <th className="px-4 py-3">USN</th>
                <th className="px-4 py-3">Sec</th>
                <th className="px-4 py-3">Attendance</th>
                <th className="px-4 py-3">CIE Marks</th>
                <th className="px-4 py-3">Backlogs</th>
                <th className="px-4 py-3">Predicted Risk</th>
                <th className="px-4 py-3">Primary Risk Driver (SHAP)</th>
                <th className="px-4 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line dark:divide-dark-line">
              {criticalStudents.slice(0, 5).map((student) => {
                const primaryDriver =
                  student.explanations?.find((e) => e.shap > 0)?.feature || 'Attendance shortage';

                return (
                  <tr
                    key={student.id}
                    className="transition hover:bg-page/40 dark:hover:bg-dark-page/40 cursor-pointer"
                    onClick={() => navigate(`/students/${student.id}`)}
                  >
                    <td className="px-4 py-3 font-semibold text-ink dark:text-dark-text">
                      {student.name}
                    </td>
                    <td className="px-4 py-3 font-mono text-caption text-muted dark:text-dark-muted">
                      {student.usn}
                    </td>
                    <td className="px-4 py-3 text-caption text-ink dark:text-dark-text">
                      {student.section}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`font-semibold ${
                          student.attendance < 75 ? 'text-risk-high' : 'text-risk-low'
                        }`}
                      >
                        {student.attendance}%
                      </span>
                    </td>
                    <td className="px-4 py-3 text-caption text-ink dark:text-dark-text">
                      {student.internalMarks} / 50
                    </td>
                    <td className="px-4 py-3">
                      <span className="rounded-pill bg-risk-high/10 px-2 py-0.5 text-caption font-semibold text-risk-high">
                        {student.backlogs} courses
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <Pill level={student.riskLevel} label={`${Math.round(student.riskScore * 100)}% High`} />
                    </td>
                    <td className="px-4 py-3 text-caption text-muted dark:text-dark-muted">
                      <span className="font-medium text-risk-high">&bull; {primaryDriver}</span>
                    </td>
                    <td className="px-4 py-3 text-right" onClick={(e) => e.stopPropagation()}>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => navigate(`/students/${student.id}`)}
                      >
                        Inspect
                      </Button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
