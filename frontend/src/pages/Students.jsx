import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  Search,
  Filter,
  Download,
  Users,
  ChevronLeft,
  ChevronRight,
  AlertCircle,
  CheckCircle2,
  ExternalLink,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Pill } from '@/components/ui/Pill';
import { STUDENTS } from '@/mocks/data';
import { formatRiskScore } from '@/utils/risk';

export default function Students() {
  const navigate = useNavigate();

  // Search & filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRiskTier, setSelectedRiskTier] = useState('ALL');
  const [selectedSection, setSelectedSection] = useState('ALL');
  const [attendanceFilter, setAttendanceFilter] = useState('ALL'); // 'ALL' or 'SHORTAGE'
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 12;

  // Filter students based on criteria
  const filteredStudents = useMemo(() => {
    return STUDENTS.filter((student) => {
      // Search matches name or USN
      const matchesSearch =
        student.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        student.usn.toLowerCase().includes(searchQuery.toLowerCase());

      // Risk level match
      const matchesRisk =
        selectedRiskTier === 'ALL' || student.riskLevel === selectedRiskTier.toLowerCase();

      // Section match
      const matchesSection =
        selectedSection === 'ALL' || student.section === selectedSection;

      // Attendance shortage match (<75%)
      const matchesAttendance =
        attendanceFilter === 'ALL' ||
        (attendanceFilter === 'SHORTAGE' && student.attendance < 75);

      return matchesSearch && matchesRisk && matchesSection && matchesAttendance;
    });
  }, [searchQuery, selectedRiskTier, selectedSection, attendanceFilter]);

  // Pagination calculation
  const totalPages = Math.ceil(filteredStudents.length / pageSize) || 1;
  const paginatedStudents = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredStudents.slice(start, start + pageSize);
  }, [filteredStudents, currentPage, pageSize]);

  // Export CSV handler
  const handleExportCSV = () => {
    const headers = ['USN', 'Name', 'Section', 'Attendance', 'InternalMarks', 'Backlogs', 'FeePaid', 'RiskScore', 'RiskLevel'];
    const rows = filteredStudents.map((s) => [
      s.usn,
      `"${s.name}"`,
      s.section,
      s.attendance,
      s.internalMarks,
      s.backlogs,
      s.feePaid ? 'Paid' : 'Pending',
      s.riskScore,
      s.riskLevel,
    ]);
    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `pesitm_students_risk_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success(`Exported ${filteredStudents.length} student records to CSV.`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-input bg-accent/10 text-accent">
              <Users className="h-4 w-4" />
            </span>
            <h1 className="font-heading text-display font-bold text-ink dark:text-dark-text">
              Student Academic Directory & Risk Registry
            </h1>
          </div>
          <p className="mt-1 text-body text-muted dark:text-dark-muted">
            PESITM 5th Semester CSE &bull; Multivariable records with XGBoost predictions & TreeSHAP attributions.
          </p>
        </div>

        <Button variant="outline" size="sm" onClick={handleExportCSV}>
          <Download className="h-3.5 w-3.5" />
          <span>Export Filtered CSV</span>
        </Button>
      </div>

      {/* Filter Bar */}
      <Card className="space-y-4">
        <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
          {/* Search Box */}
          <div className="md:col-span-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
              <input
                type="text"
                placeholder="Search by student name or USN (e.g. Rohan or 4PM21CS001)..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full rounded-input border border-line bg-surface py-2 pl-9 pr-4 text-body text-ink transition focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
              />
            </div>
          </div>

          {/* Section Selector */}
          <div>
            <select
              value={selectedSection}
              onChange={(e) => {
                setSelectedSection(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full rounded-input border border-line bg-surface px-3 py-2 text-body text-ink transition focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-surface dark:text-dark-text cursor-pointer"
            >
              <option value="ALL">All Sections (A & B)</option>
              <option value="A">Section A (32)</option>
              <option value="B">Section B (28)</option>
            </select>
          </div>

          {/* Attendance Shortage Toggle */}
          <div>
            <select
              value={attendanceFilter}
              onChange={(e) => {
                setAttendanceFilter(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full rounded-input border border-line bg-surface px-3 py-2 text-body text-ink transition focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-surface dark:text-dark-text cursor-pointer"
            >
              <option value="ALL">All Attendance Status</option>
              <option value="SHORTAGE">Shortage (&lt;75% Attendance)</option>
            </select>
          </div>
        </div>

        {/* Risk Level Filter Pills */}
        <div className="flex flex-wrap items-center gap-2 border-t border-line/60 pt-3 text-caption dark:border-dark-line/60">
          <span className="font-semibold text-muted dark:text-dark-muted">Risk Tier:</span>
          {['ALL', 'HIGH', 'MEDIUM', 'LOW'].map((tier) => {
            const count =
              tier === 'ALL'
                ? STUDENTS.length
                : STUDENTS.filter((s) => s.riskLevel === tier.toLowerCase()).length;
            const isSelected = selectedRiskTier === tier;

            return (
              <button
                key={tier}
                onClick={() => {
                  setSelectedRiskTier(tier);
                  setCurrentPage(1);
                }}
                className={`flex items-center gap-1.5 rounded-pill px-3 py-1 font-semibold transition ${
                  isSelected
                    ? 'bg-accent text-white shadow-subtle'
                    : 'bg-page text-muted hover:text-ink dark:bg-dark-page dark:text-dark-muted dark:hover:text-dark-text'
                }`}
              >
                <span>{tier === 'ALL' ? 'All Tiers' : `${tier.charAt(0) + tier.slice(1).toLowerCase()} Risk`}</span>
                <span
                  className={`rounded-full px-1.5 py-0.2 text-[10px] ${
                    isSelected ? 'bg-white/20 text-white' : 'bg-line dark:bg-dark-line'
                  }`}
                >
                  {count}
                </span>
              </button>
            );
          })}
        </div>
      </Card>

      {/* Main Student Directory Table */}
      <Card>
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
                <th className="px-4 py-3">Fee Status</th>
                <th className="px-4 py-3">Predicted Risk</th>
                <th className="px-4 py-3">Mentor</th>
                <th className="px-4 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line dark:divide-dark-line">
              {paginatedStudents.length === 0 ? (
                <tr>
                  <td colSpan={10} className="p-8 text-center text-muted">
                    No students match the selected filter criteria.
                  </td>
                </tr>
              ) : (
                paginatedStudents.map((student) => {
                  const isAttendanceShortage = student.attendance < 75;

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
                        <div className="flex items-center gap-1.5">
                          <span
                            className={`font-semibold ${
                              isAttendanceShortage ? 'text-risk-high' : 'text-risk-low'
                            }`}
                          >
                            {student.attendance}%
                          </span>
                          {isAttendanceShortage && (
                            <span
                              className="rounded-full bg-risk-high/10 p-0.5 text-risk-high"
                              title="Below mandatory 75% VTU attendance threshold"
                            >
                              <AlertCircle className="h-3.5 w-3.5" />
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-caption text-ink dark:text-dark-text">
                        {student.internalMarks} / 50
                      </td>
                      <td className="px-4 py-3">
                        {student.backlogs > 0 ? (
                          <span className="rounded-pill bg-risk-high/10 px-2 py-0.5 text-caption font-semibold text-risk-high">
                            {student.backlogs} arrears
                          </span>
                        ) : (
                          <span className="text-caption text-risk-low font-medium">0 active</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {student.feePaid ? (
                          <span className="text-caption text-muted dark:text-dark-muted">Cleared</span>
                        ) : (
                          <span className="font-semibold text-risk-medium text-caption">Due Pending</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <Pill
                          level={student.riskLevel}
                          label={`${Math.round(student.riskScore * 100)}% ${student.riskLevel}`}
                        />
                      </td>
                      <td className="px-4 py-3 text-caption text-muted dark:text-dark-muted">
                        {student.mentorName || 'Prof. Anita Rao'}
                      </td>
                      <td className="px-4 py-3 text-right" onClick={(e) => e.stopPropagation()}>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => navigate(`/students/${student.id}`)}
                        >
                          <span>Profile</span>
                          <ExternalLink className="h-3 w-3" />
                        </Button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination & Count Bar */}
        <div className="mt-4 flex flex-col items-center justify-between gap-3 sm:flex-row text-caption text-muted dark:text-dark-muted">
          <div>
            Showing <b>{paginatedStudents.length}</b> of <b>{filteredStudents.length}</b> matching students
            (Total Cohort: {STUDENTS.length})
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={currentPage === 1}
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            >
              <ChevronLeft className="h-3.5 w-3.5" />
              <span>Previous</span>
            </Button>
            <span className="font-medium text-ink dark:text-dark-text">
              Page {currentPage} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              disabled={currentPage === totalPages}
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            >
              <span>Next</span>
              <ChevronRight className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
