import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import {
  ShieldCheck,
  Users,
  BookOpen,
  School,
  KeyRound,
  UserPlus,
  Search,
  Filter,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RefreshCw,
  Trash2,
  Plus,
  Sliders,
  Sparkles,
  Activity,
  Layers,
  GraduationCap
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Pill } from '@/components/ui/Pill';
import { Modal } from '@/components/ui/Modal';
import { useAuth } from '@/context/AuthContext';
import adminService from '@/services/adminService';
import PassFailPredictionModal from '@/components/predictions/PassFailPredictionModal';

export default function AdminDashboard() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('users');
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  // Users State
  const [users, setUsers] = useState([]);
  const [userRoleFilter, setUserRoleFilter] = useState('all');
  const [userSearch, setUserSearch] = useState('');
  const [usersLoading, setUsersLoading] = useState(false);
  const [isAdminPredictionModalOpen, setIsAdminPredictionModalOpen] = useState(false);
  const [adminQuickUsn, setAdminQuickUsn] = useState('');

  // Modals State
  const [isCreateUserOpen, setIsCreateUserOpen] = useState(false);
  const [createUserForm, setCreateUserForm] = useState({
    username: '',
    email: '',
    phone: '',
    role: 'student',
    name: '',
    password: 'password123',
    usn: '',
    class_id: 1,
    employee_id: '',
    dept_id: 1,
    designation: 'Assistant Professor'
  });
  const [creatingUser, setCreatingUser] = useState(false);

  const [resetPwdUser, setResetPwdUser] = useState(null);
  const [newPassword, setNewPassword] = useState('');
  const [resettingPwd, setResettingPwd] = useState(false);

  // Academics State
  const [departments, setDepartments] = useState([]);
  const [classesList, setClassesList] = useState([]);
  const [subjectsList, setSubjectsList] = useState([]);
  const [isCreateClassOpen, setIsCreateClassOpen] = useState(false);
  const [createClassForm, setCreateClassForm] = useState({
    class_name: '',
    section: 'A',
    semester: 5,
    academic_year: '2024-25',
    dept_id: 1,
    mentor_teacher_id: ''
  });

  const [isCreateSubjectOpen, setIsCreateSubjectOpen] = useState(false);
  const [createSubjectForm, setCreateSubjectForm] = useState({
    subject_code: '',
    subject_name: '',
    semester: 5,
    credits: 3,
    dept_id: 1
  });

  // Allocations State
  const [assignments, setAssignments] = useState([]);
  const [isCreateAssignOpen, setIsCreateAssignOpen] = useState(false);
  const [assignForm, setAssignForm] = useState({ teacher_id: '', class_id: '', subject_id: '' });

  // Audit Logs State
  const [auditLogs, setAuditLogs] = useState([]);
  const [auditActionFilter, setAuditActionFilter] = useState('');

  // Initial Load
  const loadInitialData = async () => {
    setLoading(true);
    try {
      const statsData = await adminService.getStats();
      setStats(statsData);
    } catch (err) {
      console.warn('Could not load administrative stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadUsers = async () => {
    setUsersLoading(true);
    try {
      const params = {};
      if (userRoleFilter !== 'all') params.role = userRoleFilter;
      if (userSearch) params.search = userSearch;
      const res = await adminService.getUsers(params);
      setUsers(Array.isArray(res?.data) ? res.data : []);
    } catch (err) {
      console.error('Failed to load user accounts:', err);
      setUsers([]);
    } finally {
      setUsersLoading(false);
    }
  };

  const loadAcademics = async () => {
    try {
      const [depts, clss, subjs] = await Promise.all([
        adminService.getDepartments(),
        adminService.getClasses(),
        adminService.getSubjects()
      ]);
      setDepartments(depts || []);
      setClassesList(clss || []);
      setSubjectsList(subjs || []);
    } catch (err) {
      toast.error('Failed to load academic structures.');
    }
  };

  const loadAllocations = async () => {
    try {
      const data = await adminService.getAssignments();
      setAssignments(data || []);
    } catch (err) {
      toast.error('Failed to load faculty allocations.');
    }
  };

  const loadAuditLogs = async () => {
    try {
      const params = {};
      if (auditActionFilter) params.action = auditActionFilter;
      const data = await adminService.getAuditLogs(params);
      setAuditLogs(data || []);
    } catch (err) {
      toast.error('Failed to load audit logs.');
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    if (activeTab === 'users') loadUsers();
    if (activeTab === 'academics') loadAcademics();
    if (activeTab === 'allocations') {
      loadAllocations();
      loadAcademics();
    }
    if (activeTab === 'audit_logs') loadAuditLogs();
  }, [activeTab, userRoleFilter]);

  // Toggle user active status
  const handleToggleUserActive = async (targetUser) => {
    const nextStatus = !targetUser.active;
    try {
      await adminService.updateUser(targetUser.user_id, { active: nextStatus });
      toast.success(`User ${targetUser.username} ${nextStatus ? 'activated' : 'deactivated'}.`);
      await loadUsers();
      if (stats) setStats(await adminService.getStats());
    } catch (err) {
      toast.error('Failed to update user status.');
    }
  };

  // Create User
  const handleCreateUser = async (e) => {
    e.preventDefault();
    setCreatingUser(true);
    try {
      await adminService.createUser(createUserForm);
      toast.success(`Account for ${createUserForm.username} created successfully.`);
      setIsCreateUserOpen(false);
      setCreateUserForm({
        username: '',
        email: '',
        phone: '',
        role: 'student',
        name: '',
        password: 'password123',
        usn: '',
        class_id: 1,
        employee_id: '',
        dept_id: 1,
        designation: 'Assistant Professor'
      });
      await loadUsers();
      setStats(await adminService.getStats());
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to create user account.');
    } finally {
      setCreatingUser(false);
    }
  };

  // Reset Password
  const handleResetPassword = async (e) => {
    e.preventDefault();
    if (!newPassword || newPassword.length < 6) {
      toast.error('Password must be at least 6 characters.');
      return;
    }

    setResettingPwd(true);
    try {
      await adminService.resetUserPassword(resetPwdUser.user_id, newPassword);
      toast.success(`Password for ${resetPwdUser.username} reset successfully.`);
      setResetPwdUser(null);
      setNewPassword('');
    } catch (err) {
      toast.error('Failed to reset password.');
    } finally {
      setResettingPwd(false);
    }
  };

  // Create Class
  const handleCreateClass = async (e) => {
    e.preventDefault();
    try {
      await adminService.createClass(createClassForm);
      toast.success('Class division created.');
      setIsCreateClassOpen(false);
      await loadAcademics();
    } catch (err) {
      toast.error('Failed to create class.');
    }
  };

  // Create Subject
  const handleCreateSubject = async (e) => {
    e.preventDefault();
    try {
      await adminService.createSubject(createSubjectForm);
      toast.success('Subject syllabus created.');
      setIsCreateSubjectOpen(false);
      await loadAcademics();
    } catch (err) {
      toast.error('Failed to create subject.');
    }
  };

  // Create Teaching Allocation
  const handleCreateAssignment = async (e) => {
    e.preventDefault();
    try {
      await adminService.createAssignment(assignForm);
      toast.success('Faculty instructional allocation mapped.');
      setIsCreateAssignOpen(false);
      await loadAllocations();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to map assignment.');
    }
  };

  // Delete Assignment
  const handleDeleteAssignment = async (id) => {
    if (!confirm('Are you sure you want to remove this teaching allocation?')) return;
    try {
      await adminService.deleteAssignment(id);
      toast.success('Allocation deallocated.');
      await loadAllocations();
    } catch (err) {
      toast.error('Failed to remove allocation.');
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[500px] flex-col items-center justify-center space-y-4">
        <RefreshCw className="h-8 w-8 animate-spin text-accent" />
        <p className="text-body font-medium text-muted dark:text-dark-muted">
          Loading institutional administration telemetry...
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 1. Header Banner & Global Telemetry */}
      <div className="rounded-card border border-line bg-surface p-6 shadow-sm dark:border-dark-line dark:bg-dark-surface">
        <div className="flex flex-col justify-between gap-6 md:flex-row md:items-center">
          <div>
            <div className="flex items-center gap-2">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/10 text-accent">
                <ShieldCheck className="h-4 w-4" />
              </span>
              <h1 className="font-heading text-display font-bold text-ink dark:text-dark-text">
                Central Administrative Console
              </h1>
            </div>
            <p className="mt-1 text-body text-muted dark:text-dark-muted">
              PESITM Shivamogga &bull; Enterprise User Directory, Academic Allocation & Security Event Log.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={loadInitialData}
              title="Refresh System Stats"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button
              variant="primary"
              size="md"
              onClick={() => setIsAdminPredictionModalOpen(true)}
              className="flex items-center gap-2 whitespace-nowrap bg-gradient-to-r from-amber-600 via-orange-600 to-red-600 hover:from-amber-700 hover:to-orange-700 text-white shadow-md font-bold"
            >
              <Sparkles className="h-4 w-4 animate-pulse text-yellow-200" />
              AI Prediction Console
            </Button>
            <Button
              variant="outline"
              size="md"
              onClick={() => setIsCreateUserOpen(true)}
              className="flex items-center gap-2 shadow-sm"
            >
              <UserPlus className="h-4 w-4" />
              Add User Account
            </Button>
          </div>
        </div>

        {/* Global Metric Cards */}
        <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          <Card className="p-3.5 bg-page/60 border-line dark:bg-dark-page/60">
            <span className="text-xs text-muted font-medium">Total Accounts</span>
            <p className="mt-1 font-heading text-xl font-bold text-ink dark:text-dark-text">
              {stats?.users?.total || 0}
            </p>
          </Card>

          <Card className="p-3.5 bg-page/60 border-line dark:bg-dark-page/60">
            <span className="text-xs text-muted font-medium">Students</span>
            <p className="mt-1 font-heading text-xl font-bold text-accent">
              {stats?.users?.students || 0}
            </p>
          </Card>

          <Card className="p-3.5 bg-page/60 border-line dark:bg-dark-page/60">
            <span className="text-xs text-muted font-medium">Faculty Members</span>
            <p className="mt-1 font-heading text-xl font-bold text-ink dark:text-dark-text">
              {stats?.users?.teachers || 0}
            </p>
          </Card>

          <Card className="p-3.5 bg-page/60 border-line dark:bg-dark-page/60">
            <span className="text-xs text-muted font-medium">Parents</span>
            <p className="mt-1 font-heading text-xl font-bold text-ink dark:text-dark-text">
              {stats?.users?.parents || 0}
            </p>
          </Card>

          <Card className="p-3.5 bg-page/60 border-line dark:bg-dark-page/60">
            <span className="text-xs text-muted font-medium">Active Classes</span>
            <p className="mt-1 font-heading text-xl font-bold text-ink dark:text-dark-text">
              {stats?.academics?.classes || 0}
            </p>
          </Card>

          <Card className="p-3.5 bg-page/60 border-line dark:bg-dark-page/60">
            <span className="text-xs text-muted font-medium">Security Audits</span>
            <p className="mt-1 font-heading text-xl font-bold text-risk-low">
              {stats?.system?.audit_events || 0}
            </p>
          </Card>
        </div>

        {/* Tab Navigation */}
        <div className="mt-6 flex overflow-x-auto border-t border-line pt-4 scrollbar-none dark:border-dark-line">
          {[
            { id: 'users', label: 'User Directory & Access', icon: Users, count: stats?.users?.total },
            { id: 'ai_engine', label: 'AI Prediction Engine', icon: Sparkles },
            { id: 'academics', label: 'Departments & Classes', icon: School, count: stats?.academics?.classes },
            { id: 'allocations', label: 'Faculty Teaching Allocations', icon: BookOpen },
            { id: 'audit_logs', label: 'System Audit Trail', icon: Activity, count: stats?.system?.audit_events }
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
                  <span className="flex h-5 w-5 items-center justify-center rounded-full bg-accent/15 text-[10px] text-accent">
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* 2. TAB: Users Directory */}
      {activeTab === 'users' && (
        <div className="space-y-4">
          <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
            {/* Search Input */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted" />
              <input
                type="text"
                placeholder="Search by username, email, phone..."
                value={userSearch}
                onChange={(e) => setUserSearch(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && loadUsers()}
                className="w-full rounded-input border border-line bg-surface py-2 pl-9 pr-4 text-caption text-ink placeholder:text-muted/60 focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
              />
            </div>

            {/* Role Filter Pills */}
            <div className="flex flex-wrap items-center gap-1.5">
              {['all', 'student', 'teacher', 'parent', 'admin', 'principal'].map((r) => (
                <button
                  key={r}
                  onClick={() => setUserRoleFilter(r)}
                  className={`rounded-input px-3 py-1 text-xs font-semibold uppercase tracking-wider transition-colors ${
                    userRoleFilter === r
                      ? 'bg-accent text-white'
                      : 'border border-line bg-surface text-muted hover:text-ink dark:border-dark-line dark:bg-dark-surface'
                  }`}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>

          {/* User Table */}
          <Card className="p-0 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-caption">
                <thead className="border-b border-line bg-page text-muted dark:border-dark-line dark:bg-dark-page">
                  <tr>
                    <th className="py-3 px-4 font-semibold">User</th>
                    <th className="py-3 px-4 font-semibold">Role</th>
                    <th className="py-3 px-4 font-semibold">Email & Phone</th>
                    <th className="py-3 px-4 font-semibold">Associated Profile</th>
                    <th className="py-3 px-4 font-semibold text-center">Status</th>
                    <th className="py-3 px-4 font-semibold text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line dark:divide-dark-line">
                  {usersLoading ? (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-muted">
                        <RefreshCw className="mx-auto h-6 w-6 animate-spin text-accent" />
                        <span className="mt-2 block">Loading user directory...</span>
                      </td>
                    </tr>
                  ) : users.length > 0 ? (
                    users.map((u) => (
                      <tr key={u.user_id} className="hover:bg-page/50 dark:hover:bg-dark-page/50 transition-colors">
                        <td className="py-3 px-4">
                          <strong className="font-heading font-bold text-ink dark:text-dark-text block">
                            {u.profile_name || u.username}
                          </strong>
                          <span className="font-mono text-xs text-muted">@{u.username}</span>
                        </td>
                        <td className="py-3 px-4">
                          <Pill variant="neutral" className="uppercase font-mono text-[10px]">
                            {u.role}
                          </Pill>
                        </td>
                        <td className="py-3 px-4 text-xs text-muted">
                          <div>{u.email}</div>
                          {u.phone && <div>{u.phone}</div>}
                        </td>
                        <td className="py-3 px-4 text-xs">
                          {u.usn && <span className="font-mono font-semibold text-accent">USN: {u.usn}</span>}
                          {u.employee_id && <span className="font-mono font-semibold text-accent">EmpID: {u.employee_id}</span>}
                          {u.wards_count !== undefined && <span className="text-muted">{u.wards_count} Ward(s)</span>}
                        </td>
                        <td className="py-3 px-4 text-center">
                          <span
                            className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold ${
                              u.active
                                ? 'bg-risk-low/10 text-risk-low'
                                : 'bg-risk-high/10 text-risk-high'
                            }`}
                          >
                            {u.active ? <CheckCircle2 className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
                            {u.active ? 'Active' : 'Deactivated'}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <div className="flex items-center justify-end gap-1.5">
                            <Button
                              variant="outline"
                              size="xs"
                              onClick={() => handleToggleUserActive(u)}
                              title={u.active ? 'Deactivate Account' : 'Reactivate Account'}
                            >
                              {u.active ? 'Deactivate' : 'Activate'}
                            </Button>
                            <Button
                              variant="outline"
                              size="xs"
                              onClick={() => {
                                setResetPwdUser(u);
                                setNewPassword('');
                              }}
                              title="Reset Password Override"
                            >
                              <KeyRound className="h-3.5 w-3.5" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-muted">
                        No accounts match the criteria.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {/* 3. TAB: Academics (Departments, Classes, Subjects) */}
      {activeTab === 'academics' && (
        <div className="space-y-6">
          {/* Departments Grid */}
          <Card className="p-6">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="text-section">Academic Departments</CardTitle>
              <CardDescription>Affiliated VTU engineering programs and department heads.</CardDescription>
            </CardHeader>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {departments.map((d) => (
                <div key={d.dept_id} className="rounded-input border border-line bg-page p-4 dark:border-dark-line dark:bg-dark-page">
                  <span className="font-mono text-xs font-bold text-accent">{d.dept_code}</span>
                  <h4 className="font-heading font-bold text-ink dark:text-dark-text mt-1">{d.name}</h4>
                  <p className="mt-2 text-caption text-muted">HoD: <strong>{d.hod_name}</strong></p>
                  <p className="mt-0.5 text-xs text-muted">{d.classes_count} Classes &bull; {d.subjects_count} Subjects</p>
                </div>
              ))}
            </div>
          </Card>

          {/* Classes & Divisions */}
          <Card className="p-6">
            <div className="flex items-center justify-between border-b border-line pb-4 dark:border-dark-line">
              <div>
                <CardTitle className="text-section">Class Divisions & Cohorts</CardTitle>
                <CardDescription>Section units with assigned faculty mentors.</CardDescription>
              </div>
              <Button variant="primary" size="sm" onClick={() => setIsCreateClassOpen(true)}>
                <Plus className="h-4 w-4 mr-1" /> Add Class
              </Button>
            </div>

            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-left text-caption">
                <thead className="border-b border-line bg-page text-muted dark:border-dark-line dark:bg-dark-page">
                  <tr>
                    <th className="py-2.5 px-3">Class Name</th>
                    <th className="py-2.5 px-3">Section</th>
                    <th className="py-2.5 px-3">Semester</th>
                    <th className="py-2.5 px-3">Department</th>
                    <th className="py-2.5 px-3">Faculty Mentor</th>
                    <th className="py-2.5 px-3 text-center">Enrolled</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line dark:divide-dark-line">
                  {classesList.map((c) => (
                    <tr key={c.class_id}>
                      <td className="py-3 px-3 font-semibold text-ink dark:text-dark-text">{c.class_name}</td>
                      <td className="py-3 px-3 font-mono font-bold text-accent">{c.section}</td>
                      <td className="py-3 px-3">Sem {c.semester}</td>
                      <td className="py-3 px-3 text-muted">{c.dept_name}</td>
                      <td className="py-3 px-3">{c.mentor_name}</td>
                      <td className="py-3 px-3 text-center font-bold text-ink dark:text-dark-text">{c.enrolled_students}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Subjects Syllabus */}
          <Card className="p-6">
            <div className="flex items-center justify-between border-b border-line pb-4 dark:border-dark-line">
              <div>
                <CardTitle className="text-section">Curriculum Subjects</CardTitle>
                <CardDescription>VTU syllabus courses with assigned credit weights.</CardDescription>
              </div>
              <Button variant="primary" size="sm" onClick={() => setIsCreateSubjectOpen(true)}>
                <Plus className="h-4 w-4 mr-1" /> Add Subject
              </Button>
            </div>

            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-left text-caption">
                <thead className="border-b border-line bg-page text-muted dark:border-dark-line dark:bg-dark-page">
                  <tr>
                    <th className="py-2.5 px-3">Code</th>
                    <th className="py-2.5 px-3">Course Title</th>
                    <th className="py-2.5 px-3">Semester</th>
                    <th className="py-2.5 px-3">Credits</th>
                    <th className="py-2.5 px-3">Department</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line dark:divide-dark-line">
                  {subjectsList.map((s) => (
                    <tr key={s.subject_id}>
                      <td className="py-3 px-3 font-mono font-bold text-accent">{s.subject_code}</td>
                      <td className="py-3 px-3 font-medium text-ink dark:text-dark-text">{s.subject_name}</td>
                      <td className="py-3 px-3">Sem {s.semester}</td>
                      <td className="py-3 px-3">{s.credits} Credits</td>
                      <td className="py-3 px-3 text-muted">{s.dept_name}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {/* 4. TAB: Faculty Allocations */}
      {activeTab === 'allocations' && (
        <Card className="p-6">
          <div className="flex items-center justify-between border-b border-line pb-4 dark:border-dark-line">
            <div>
              <CardTitle className="text-section">Faculty Instructional Allocations</CardTitle>
              <CardDescription>Mapping teachers to classes and subjects (governs teacher portal access scopes).</CardDescription>
            </div>
            <Button variant="primary" size="sm" onClick={() => setIsCreateAssignOpen(true)}>
              <Plus className="h-4 w-4 mr-1" /> Map Faculty to Subject
            </Button>
          </div>

          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-caption">
              <thead className="border-b border-line bg-page text-muted dark:border-dark-line dark:bg-dark-page">
                <tr>
                  <th className="py-2.5 px-3">Faculty Name</th>
                  <th className="py-2.5 px-3">Employee ID</th>
                  <th className="py-2.5 px-3">Class & Section</th>
                  <th className="py-2.5 px-3">Assigned Course</th>
                  <th className="py-2.5 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line dark:divide-dark-line">
                {assignments.map((a) => (
                  <tr key={a.id}>
                    <td className="py-3 px-3 font-semibold text-ink dark:text-dark-text">{a.teacher_name}</td>
                    <td className="py-3 px-3 font-mono text-muted">{a.employee_id}</td>
                    <td className="py-3 px-3">{a.class_name} (Sec {a.section})</td>
                    <td className="py-3 px-3">
                      <span className="font-mono text-xs text-accent font-semibold">{a.subject_code}</span> &bull; {a.subject_name}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <Button
                        variant="outline"
                        size="xs"
                        onClick={() => handleDeleteAssignment(a.id)}
                        className="text-risk-high hover:bg-risk-high/10"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* 5. TAB: System Audit Trail */}
      {activeTab === 'audit_logs' && (
        <Card className="p-6">
          <CardHeader className="p-0 pb-4">
            <CardTitle className="text-section">System Security & Operational Event Log</CardTitle>
            <CardDescription>Immutable tracking of authentication attempts, marks modifications, and administrative operations.</CardDescription>
          </CardHeader>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-caption">
              <thead className="border-b border-line bg-page text-muted dark:border-dark-line dark:bg-dark-page">
                <tr>
                  <th className="py-2.5 px-3">Timestamp</th>
                  <th className="py-2.5 px-3">Action Event</th>
                  <th className="py-2.5 px-3">User Role</th>
                  <th className="py-2.5 px-3">Target Entity</th>
                  <th className="py-2.5 px-3 font-mono">IP Address</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line dark:divide-dark-line">
                {auditLogs.map((log) => (
                  <tr key={log.id}>
                    <td className="py-3 px-3 text-xs text-muted whitespace-nowrap">
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-3 font-mono font-bold text-accent text-xs">
                      {log.action}
                    </td>
                    <td className="py-3 px-3">
                      <Pill variant="neutral" className="uppercase font-mono text-[10px]">
                        {log.role || 'System'}
                      </Pill>
                    </td>
                    <td className="py-3 px-3 text-xs text-muted">
                      {log.target_type ? `${log.target_type} #${log.target_id || ''}` : '-'}
                    </td>
                    <td className="py-3 px-3 font-mono text-xs text-muted">
                      {log.ip || '127.0.0.1'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* MODAL: Create User */}
      {isCreateUserOpen && (
        <Modal
          isOpen={true}
          onClose={() => setIsCreateUserOpen(false)}
          title="Create New Institutional User Account"
        >
          <form onSubmit={handleCreateUser} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-caption font-semibold text-muted">Username *</label>
                <input
                  type="text"
                  required
                  value={createUserForm.username}
                  onChange={(e) => setCreateUserForm({ ...createUserForm, username: e.target.value })}
                  placeholder="e.g. 4PM22CS099 or prof.sharma"
                  className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                />
              </div>

              <div>
                <label className="block text-caption font-semibold text-muted">Email *</label>
                <input
                  type="email"
                  required
                  value={createUserForm.email}
                  onChange={(e) => setCreateUserForm({ ...createUserForm, email: e.target.value })}
                  placeholder="name@pesitm.edu"
                  className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                />
              </div>

              <div>
                <label className="block text-caption font-semibold text-muted">Full Name *</label>
                <input
                  type="text"
                  required
                  value={createUserForm.name}
                  onChange={(e) => setCreateUserForm({ ...createUserForm, name: e.target.value })}
                  placeholder="Official Name"
                  className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                />
              </div>

              <div>
                <label className="block text-caption font-semibold text-muted">Portal Role *</label>
                <select
                  value={createUserForm.role}
                  onChange={(e) => setCreateUserForm({ ...createUserForm, role: e.target.value })}
                  className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                >
                  <option value="student">Student</option>
                  <option value="teacher">Teacher</option>
                  <option value="parent">Parent</option>
                  <option value="admin">Administrator</option>
                  <option value="principal">Principal</option>
                </select>
              </div>

              <div>
                <label className="block text-caption font-semibold text-muted">Contact Phone</label>
                <input
                  type="text"
                  value={createUserForm.phone}
                  onChange={(e) => setCreateUserForm({ ...createUserForm, phone: e.target.value })}
                  placeholder="+91 98450 XXXXX"
                  className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                />
              </div>

              <div>
                <label className="block text-caption font-semibold text-muted">Initial Password *</label>
                <input
                  type="text"
                  required
                  value={createUserForm.password}
                  onChange={(e) => setCreateUserForm({ ...createUserForm, password: e.target.value })}
                  className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                />
              </div>
            </div>

            {/* Role specific inputs */}
            {createUserForm.role === 'student' && (
              <div className="grid grid-cols-2 gap-3 border-t border-line pt-3 dark:border-dark-line">
                <div>
                  <label className="block text-caption font-semibold text-muted">University USN *</label>
                  <input
                    type="text"
                    required
                    value={createUserForm.usn}
                    onChange={(e) => setCreateUserForm({ ...createUserForm, usn: e.target.value })}
                    placeholder="4PM21CS001"
                    className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text uppercase"
                  />
                </div>
                <div>
                  <label className="block text-caption font-semibold text-muted">Enrolled Class ID</label>
                  <input
                    type="number"
                    value={createUserForm.class_id}
                    onChange={(e) => setCreateUserForm({ ...createUserForm, class_id: parseInt(e.target.value) || 1 })}
                    className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                  />
                </div>
              </div>
            )}

            {createUserForm.role === 'teacher' && (
              <div className="grid grid-cols-2 gap-3 border-t border-line pt-3 dark:border-dark-line">
                <div>
                  <label className="block text-caption font-semibold text-muted">Employee ID *</label>
                  <input
                    type="text"
                    required
                    value={createUserForm.employee_id}
                    onChange={(e) => setCreateUserForm({ ...createUserForm, employee_id: e.target.value })}
                    placeholder="EMP-CSE-99"
                    className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                  />
                </div>
                <div>
                  <label className="block text-caption font-semibold text-muted">Designation</label>
                  <input
                    type="text"
                    value={createUserForm.designation}
                    onChange={(e) => setCreateUserForm({ ...createUserForm, designation: e.target.value })}
                    className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                  />
                </div>
              </div>
            )}

            <div className="flex justify-end gap-2 pt-3">
              <Button variant="outline" type="button" onClick={() => setIsCreateUserOpen(false)}>
                Cancel
              </Button>
              <Button variant="primary" type="submit" loading={creatingUser}>
                Create User
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* MODAL: Reset Password */}
      {resetPwdUser && (
        <Modal
          isOpen={true}
          onClose={() => setResetPwdUser(null)}
          title={`Administrative Password Reset: ${resetPwdUser.username}`}
        >
          <form onSubmit={handleResetPassword} className="space-y-4">
            <p className="text-caption text-muted">
              Enter a new secure password for <strong>{resetPwdUser.profile_name || resetPwdUser.username}</strong> ({resetPwdUser.email}).
            </p>
            <div>
              <label className="block text-caption font-semibold text-muted">New Password *</label>
              <input
                type="text"
                required
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Minimum 6 characters"
                className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" type="button" onClick={() => setResetPwdUser(null)}>
                Cancel
              </Button>
              <Button variant="primary" type="submit" loading={resettingPwd}>
                Update Password
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* MODAL: Create Class */}
      {isCreateClassOpen && (
        <Modal
          isOpen={true}
          onClose={() => setIsCreateClassOpen(false)}
          title="Add New Academic Class Division"
        >
          <form onSubmit={handleCreateClass} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-caption font-semibold text-muted">Class Name *</label>
                <input
                  type="text"
                  required
                  value={createClassForm.class_name}
                  onChange={(e) => setCreateClassForm({ ...createClassForm, class_name: e.target.value })}
                  placeholder="e.g. 5th Sem CSE"
                  className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                />
              </div>
              <div>
                <label className="block text-caption font-semibold text-muted">Section *</label>
                <input
                  type="text"
                  required
                  value={createClassForm.section}
                  onChange={(e) => setCreateClassForm({ ...createClassForm, section: e.target.value })}
                  placeholder="A or B"
                  className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                />
              </div>
              <div>
                <label className="block text-caption font-semibold text-muted">Semester (1-8)</label>
                <input
                  type="number"
                  min="1"
                  max="8"
                  value={createClassForm.semester}
                  onChange={(e) => setCreateClassForm({ ...createClassForm, semester: parseInt(e.target.value) || 1 })}
                  className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                />
              </div>
              <div>
                <label className="block text-caption font-semibold text-muted">Academic Year</label>
                <input
                  type="text"
                  value={createClassForm.academic_year}
                  onChange={(e) => setCreateClassForm({ ...createClassForm, academic_year: e.target.value })}
                  className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" type="button" onClick={() => setIsCreateClassOpen(false)}>
                Cancel
              </Button>
              <Button variant="primary" type="submit">
                Create Class
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* MODAL: Create Subject */}
      {isCreateSubjectOpen && (
        <Modal
          isOpen={true}
          onClose={() => setIsCreateSubjectOpen(false)}
          title="Add New Syllabus Course / Subject"
        >
          <form onSubmit={handleCreateSubject} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-caption font-semibold text-muted">Course Code *</label>
                <input
                  type="text"
                  required
                  value={createSubjectForm.subject_code}
                  onChange={(e) => setCreateSubjectForm({ ...createSubjectForm, subject_code: e.target.value })}
                  placeholder="21CS51"
                  className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption uppercase dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                />
              </div>
              <div>
                <label className="block text-caption font-semibold text-muted">Course Title *</label>
                <input
                  type="text"
                  required
                  value={createSubjectForm.subject_name}
                  onChange={(e) => setCreateSubjectForm({ ...createSubjectForm, subject_name: e.target.value })}
                  placeholder="Database Systems"
                  className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                />
              </div>
              <div>
                <label className="block text-caption font-semibold text-muted">Semester</label>
                <input
                  type="number"
                  min="1"
                  max="8"
                  value={createSubjectForm.semester}
                  onChange={(e) => setCreateSubjectForm({ ...createSubjectForm, semester: parseInt(e.target.value) || 1 })}
                  className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                />
              </div>
              <div>
                <label className="block text-caption font-semibold text-muted">Credits</label>
                <input
                  type="number"
                  min="1"
                  max="6"
                  value={createSubjectForm.credits}
                  onChange={(e) => setCreateSubjectForm({ ...createSubjectForm, credits: parseInt(e.target.value) || 3 })}
                  className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" type="button" onClick={() => setIsCreateSubjectOpen(false)}>
                Cancel
              </Button>
              <Button variant="primary" type="submit">
                Save Subject
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* MODAL: Create Allocation */}
      {isCreateAssignOpen && (
        <Modal
          isOpen={true}
          onClose={() => setIsCreateAssignOpen(false)}
          title="Map Faculty Member to Subject & Class"
        >
          <form onSubmit={handleCreateAssignment} className="space-y-4">
            <div>
              <label className="block text-caption font-semibold text-muted">Teacher ID *</label>
              <input
                type="number"
                required
                value={assignForm.teacher_id}
                onChange={(e) => setAssignForm({ ...assignForm, teacher_id: parseInt(e.target.value) })}
                placeholder="Teacher ID"
                className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
              />
            </div>
            <div>
              <label className="block text-caption font-semibold text-muted">Class ID *</label>
              <input
                type="number"
                required
                value={assignForm.class_id}
                onChange={(e) => setAssignForm({ ...assignForm, class_id: parseInt(e.target.value) })}
                placeholder="Class ID"
                className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
              />
            </div>
            <div>
              <label className="block text-caption font-semibold text-muted">Subject ID *</label>
              <input
                type="number"
                required
                value={assignForm.subject_id}
                onChange={(e) => setAssignForm({ ...assignForm, subject_id: parseInt(e.target.value) })}
                placeholder="Subject ID"
                className="mt-1 w-full rounded-input border border-line bg-surface px-3 py-1.5 text-caption dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" type="button" onClick={() => setIsCreateAssignOpen(false)}>
                Cancel
              </Button>
              <Button variant="primary" type="submit">
                Confirm Mapping
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* AI Prediction Engine Control Tab */}
      {activeTab === 'ai_engine' && (
        <div className="space-y-6">
          <Card className="p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-line pb-4 dark:border-dark-line">
              <div>
                <div className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-accent animate-pulse" />
                  <CardTitle className="text-section">Institutional AI Prediction Engine & Controls</CardTitle>
                </div>
                <CardDescription>
                  Production ML pipeline benchmarking 5 algorithms (XGBoost, Random Forest, Gradient Boosting, Decision Tree, Logistic Regression) on past marks to predict VTU exam outcomes.
                </CardDescription>
              </div>
              <Button
                variant="primary"
                onClick={() => setIsAdminPredictionModalOpen(true)}
                className="bg-gradient-to-r from-amber-600 to-orange-600 text-white font-bold flex items-center gap-2 shadow-md shrink-0"
              >
                <Sliders className="h-4 w-4" />
                Launch Pass/Fail Simulator
              </Button>
            </div>

            {/* Model Architecture Specs */}
            <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="rounded-xl border border-line bg-page p-4 dark:border-dark-line dark:bg-dark-page">
                <span className="text-xs font-semibold text-muted">Champion Classifier</span>
                <p className="mt-1 font-heading text-xl font-bold text-accent">XGBoost</p>
                <span className="text-[10px] text-muted">Gradient Boosted Decision Trees</span>
              </div>

              <div className="rounded-xl border border-line bg-page p-4 dark:border-dark-line dark:bg-dark-page">
                <span className="text-xs font-semibold text-muted">Test Set Accuracy</span>
                <p className="mt-1 font-heading text-xl font-bold text-emerald-600">98.33%</p>
                <span className="text-[10px] text-muted">5-Fold Stratified Cross Validation</span>
              </div>

              <div className="rounded-xl border border-line bg-page p-4 dark:border-dark-line dark:bg-dark-page">
                <span className="text-xs font-semibold text-muted">Macro F1-Score</span>
                <p className="mt-1 font-heading text-xl font-bold text-ink dark:text-dark-text">0.9892</p>
                <span className="text-[10px] text-muted">ROC-AUC: 0.9989</span>
              </div>

              <div className="rounded-xl border border-line bg-page p-4 dark:border-dark-line dark:bg-dark-page">
                <span className="text-xs font-semibold text-muted">Input Feature Vectors</span>
                <p className="mt-1 font-heading text-xl font-bold text-ink dark:text-dark-text">19 Features</p>
                <span className="text-[10px] text-muted">Past IA + SGPA + CGPA + Attendance</span>
              </div>
            </div>

            {/* Quick Student Prediction Console */}
            <div className="mt-6 rounded-xl border border-line bg-surface p-5 dark:border-dark-line dark:bg-dark-surface space-y-3">
              <h4 className="font-heading text-subheading font-bold text-ink dark:text-dark-text">
                Quick Single-Student Prediction Lookup
              </h4>
              <p className="text-xs text-muted">
                Enter any student's USN (e.g., 4PM21CS001, 4PM23CS002) to evaluate their live pass/fail outcome.
              </p>
              <div className="flex gap-3 max-w-md">
                <input
                  type="text"
                  placeholder="Enter Student USN..."
                  value={adminQuickUsn}
                  onChange={(e) => setAdminQuickUsn(e.target.value.toUpperCase())}
                  className="flex-1 rounded-input border border-line bg-page px-3.5 py-2 font-mono text-sm uppercase dark:border-dark-line dark:bg-dark-page dark:text-dark-text"
                />
                <Button
                  variant="primary"
                  onClick={() => setIsAdminPredictionModalOpen(true)}
                  className="font-bold flex items-center gap-1.5"
                >
                  <Sparkles className="h-4 w-4" /> Evaluate
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Admin Pass/Fail Prediction Intelligence Modal */}
      <PassFailPredictionModal
        isOpen={isAdminPredictionModalOpen}
        onClose={() => setIsAdminPredictionModalOpen(false)}
        initialUsn={adminQuickUsn || "4PM21CS001"}
        title="Institutional Examination Pass/Fail Intelligence"
      />
    </div>
  );
}
