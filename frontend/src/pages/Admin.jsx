import React, { useState } from 'react';
import toast from 'react-hot-toast';
import {
  ShieldCheck,
  Cpu,
  Users,
  Database,
  RefreshCw,
  Plus,
  Download,
  CheckCircle2,
  AlertCircle,
  FileText,
  Sliders,
  Sparkles,
  Lock,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input, Select } from '@/components/ui/Input';
import { Pill } from '@/components/ui/Pill';
import { Modal } from '@/components/ui/Modal';
import { INITIAL_USERS, INITIAL_MODEL_INFO, CLASSES } from '@/mocks/data';
import { formatDate } from '@/utils/format';

export default function Admin() {
  const [modelInfo, setModelInfo] = useState(INITIAL_MODEL_INFO);
  const [users, setUsers] = useState(INITIAL_USERS);
  const [selectedRoleFilter, setSelectedRoleFilter] = useState('all');
  const [isRetrainModalOpen, setIsRetrainModalOpen] = useState(false);
  const [isAddUserModalOpen, setIsAddUserModalOpen] = useState(false);
  const [isRetraining, setIsRetraining] = useState(false);
  const [retrainProgress, setRetrainProgress] = useState(0);

  // Retrain hyperparameters form state
  const [hyperparams, setHyperparams] = useState({
    nEstimators: 150,
    maxDepth: 6,
    learningRate: 0.08,
    smoteEnabled: true,
    cvFolds: 5,
  });

  // New user form state
  const [newUser, setNewUser] = useState({
    name: '',
    username: '',
    email: '',
    role: 'teacher',
    department: 'CSE',
    usn: '',
  });

  // Filtered users list
  const filteredUsers =
    selectedRoleFilter === 'all'
      ? users
      : users.filter((u) => u.role === selectedRoleFilter);

  // Trigger retrain simulation
  const handleStartRetraining = () => {
    setIsRetraining(true);
    setRetrainProgress(10);

    const interval = setInterval(() => {
      setRetrainProgress((prev) => {
        if (prev >= 95) {
          clearInterval(interval);
          setTimeout(() => {
            setIsRetraining(false);
            setIsRetrainModalOpen(false);
            setRetrainProgress(0);
            setModelInfo((prevModel) => ({
              ...prevModel,
              version: 'v1.0.1',
              accuracy: 0.984,
              f1Macro: 0.9782,
              trainedAt: new Date().toISOString(),
            }));
            toast.success(
              'Model retraining completed! XGBoost v1.0.1 deployed with 98.4% accuracy.'
            );
          }, 600);
          return 100;
        }
        return prev + 18;
      });
    }, 400);
  };

  // Add User Handler
  const handleAddUser = (e) => {
    e.preventDefault();
    if (!newUser.name || !newUser.email) {
      toast.error('Please provide a name and valid email address.');
      return;
    }
    const created = {
      id: users.length + 1,
      ...newUser,
      active: true,
    };
    setUsers([...users, created]);
    setIsAddUserModalOpen(false);
    setNewUser({
      name: '',
      username: '',
      email: '',
      role: 'teacher',
      department: 'CSE',
      usn: '',
    });
    toast.success(`User "${created.name}" created successfully with role ${created.role}.`);
  };

  // Toggle user active status
  const toggleUserActive = (id) => {
    setUsers(
      users.map((u) => {
        if (u.id === id) {
          const updated = !u.active;
          toast.success(`User ${u.name} is now ${updated ? 'Active' : 'Deactivated'}.`);
          return { ...u, active: updated };
        }
        return u;
      })
    );
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-input bg-accent/10 text-accent">
              <ShieldCheck className="h-4 w-4" />
            </span>
            <h1 className="font-heading text-display font-bold text-ink dark:text-dark-text">
              System Administration & ML Governance
            </h1>
          </div>
          <p className="mt-1 text-body text-muted dark:text-dark-muted">
            PESITM Shivamogga institutional portal &bull; Model versioning, hyperparameter controls, RBAC, and audit trail.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => toast.success('Diagnostics check passed: MySQL connected, Flask ML healthy.')}
          >
            <CheckCircle2 className="h-3.5 w-3.5 text-risk-low" />
            <span>Health Check</span>
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => setIsRetrainModalOpen(true)}
          >
            <RefreshCw className="h-3.5 w-3.5" />
            <span>Retrain Model</span>
          </Button>
        </div>
      </div>

      {/* Top System Health & Scale KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-input bg-accent/10 text-accent">
            <Users className="h-6 w-6" />
          </div>
          <div>
            <p className="text-caption font-medium text-muted dark:text-dark-muted">Monitored Students</p>
            <p className="font-heading text-heading font-bold text-ink dark:text-dark-text">60 Active</p>
            <p className="text-[11px] text-muted">5th Sem CSE (Sec A & B)</p>
          </div>
        </Card>

        <Card className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-input bg-risk-low/10 text-risk-low">
            <Cpu className="h-6 w-6" />
          </div>
          <div>
            <p className="text-caption font-medium text-muted dark:text-dark-muted">Serving ML Engine</p>
            <p className="font-heading text-heading font-bold text-ink dark:text-dark-text">
              XGBoost {modelInfo.version}
            </p>
            <p className="text-[11px] text-risk-low font-semibold">98.0% Accuracy &bull; Active</p>
          </div>
        </Card>

        <Card className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-input bg-risk-medium/10 text-risk-medium">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <div>
            <p className="text-caption font-medium text-muted dark:text-dark-muted">Registered Faculty</p>
            <p className="font-heading text-heading font-bold text-ink dark:text-dark-text">
              {users.filter((u) => u.role === 'teacher').length} Mentors
            </p>
            <p className="text-[11px] text-muted">CSE Department Staff</p>
          </div>
        </Card>

        <Card className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-input bg-page text-ink dark:bg-dark-page dark:text-dark-text">
            <Database className="h-6 w-6" />
          </div>
          <div>
            <p className="text-caption font-medium text-muted dark:text-dark-muted">Inference Invocations</p>
            <p className="font-heading text-heading font-bold text-ink dark:text-dark-text">1,840 Records</p>
            <p className="text-[11px] text-muted">Attendance + CIE Logged</p>
          </div>
        </Card>
      </div>

      {/* Machine Learning Model Performance & Governance Card */}
      <Card>
        <CardHeader>
          <div>
            <div className="flex items-center gap-2">
              <CardTitle>Machine Learning Model Governance & Validation</CardTitle>
              <span className="rounded-pill bg-risk-low/10 px-2.5 py-0.5 text-[11px] font-semibold text-risk-low border border-risk-low/30">
                Production Serving: {modelInfo.version}
              </span>
            </div>
            <CardDescription>
              Extreme Gradient Boosting (XGBoost) model evaluated with 5-Fold Stratified Cross-Validation on Indian engineering college schema + UCI benchmark.
            </CardDescription>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                toast.success('Downloading model card specification (VTU-XGB-2024.json)...');
              }}
            >
              <Download className="h-3.5 w-3.5" />
              <span>Model Card</span>
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={() => setIsRetrainModalOpen(true)}
            >
              <Sliders className="h-3.5 w-3.5" />
              <span>Configure Hyperparameters</span>
            </Button>
          </div>
        </CardHeader>

        {/* ML Metric Grids */}
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          <div className="rounded-input border border-line bg-page/40 p-3 text-center dark:border-dark-line dark:bg-dark-surface/40">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-muted dark:text-dark-muted">
              Accuracy
            </p>
            <p className="font-heading text-2xl font-bold text-ink dark:text-dark-text">
              {(modelInfo.accuracy * 100).toFixed(1)}%
            </p>
            <p className="text-[10px] text-risk-low font-medium">&plusmn;0.8% 5-fold CV</p>
          </div>

          <div className="rounded-input border border-line bg-page/40 p-3 text-center dark:border-dark-line dark:bg-dark-surface/40">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-muted dark:text-dark-muted">
              Macro F1-Score
            </p>
            <p className="font-heading text-2xl font-bold text-accent">
              {modelInfo.f1Macro.toFixed(4)}
            </p>
            <p className="text-[10px] text-muted">Imbalance weighted</p>
          </div>

          <div className="rounded-input border border-line bg-page/40 p-3 text-center dark:border-dark-line dark:bg-dark-surface/40">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-muted dark:text-dark-muted">
              Precision (Macro)
            </p>
            <p className="font-heading text-2xl font-bold text-ink dark:text-dark-text">
              {(modelInfo.precisionMacro * 100).toFixed(1)}%
            </p>
            <p className="text-[10px] text-muted">Low false alarms</p>
          </div>

          <div className="rounded-input border border-line bg-page/40 p-3 text-center dark:border-dark-line dark:bg-dark-surface/40">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-muted dark:text-dark-muted">
              Recall (Macro)
            </p>
            <p className="font-heading text-2xl font-bold text-ink dark:text-dark-text">
              {(modelInfo.recallMacro * 100).toFixed(1)}%
            </p>
            <p className="text-[10px] text-risk-low font-medium">97.4% High-risk caught</p>
          </div>

          <div className="rounded-input border border-line bg-page/40 p-3 text-center dark:border-dark-line dark:bg-dark-surface/40">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-muted dark:text-dark-muted">
              ROC-AUC Area
            </p>
            <p className="font-heading text-2xl font-bold text-ink dark:text-dark-text">
              {modelInfo.rocAuc.toFixed(4)}
            </p>
            <p className="text-[10px] text-muted">One-vs-Rest</p>
          </div>

          <div className="rounded-input border border-line bg-page/40 p-3 text-center dark:border-dark-line dark:bg-dark-surface/40">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-muted dark:text-dark-muted">
              GPA Regressor R&sup2;
            </p>
            <p className="font-heading text-2xl font-bold text-ink dark:text-dark-text">
              {modelInfo.regressorR2.toFixed(4)}
            </p>
            <p className="text-[10px] text-muted">MAE: {modelInfo.regressorMae}</p>
          </div>
        </div>

        {/* Technical Architecture Specs */}
        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 rounded-input border border-line bg-surface p-3.5 text-caption dark:border-dark-line dark:bg-dark-surface">
          <div>
            <span className="font-semibold text-muted dark:text-dark-muted">Preprocessing Pipeline:</span>
            <p className="font-medium text-ink dark:text-dark-text">IQR Filtering &bull; QuantileTransform &bull; SMOTE (Train)</p>
          </div>
          <div>
            <span className="font-semibold text-muted dark:text-dark-muted">Feature Attribution:</span>
            <p className="font-medium text-ink dark:text-dark-text">TreeSHAP Local Vectors &bull; Additive Attributions</p>
          </div>
          <div>
            <span className="font-semibold text-muted dark:text-dark-muted">Last Model Retraining:</span>
            <p className="font-medium text-ink dark:text-dark-text">{formatDate(modelInfo.trainedAt)}</p>
          </div>
          <div>
            <span className="font-semibold text-muted dark:text-dark-muted">Storage Artifact:</span>
            <p className="font-mono text-[11px] text-ink dark:text-dark-text">ml-service/models/xgboost_risk_v1.joblib</p>
          </div>
        </div>
      </Card>

      {/* User Accounts & Role-Based Access Control (RBAC) */}
      <Card>
        <CardHeader>
          <div>
            <CardTitle>User Accounts & Role Permissions</CardTitle>
            <CardDescription>
              Manage accounts for Administrators, Faculty Mentors, Students, and Parents.
            </CardDescription>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* Filter Buttons */}
            <div className="flex rounded-input border border-line bg-page p-0.5 text-caption dark:border-dark-line dark:bg-dark-page">
              {['all', 'admin', 'teacher', 'student', 'parent'].map((role) => (
                <button
                  key={role}
                  onClick={() => setSelectedRoleFilter(role)}
                  className={`rounded-input px-2.5 py-1 font-medium capitalize transition ${
                    selectedRoleFilter === role
                      ? 'bg-surface text-ink shadow-sm dark:bg-dark-surface dark:text-dark-text'
                      : 'text-muted hover:text-ink dark:text-dark-muted dark:hover:text-dark-text'
                  }`}
                >
                  {role === 'all' ? 'All Roles' : role}
                </button>
              ))}
            </div>

            <Button
              variant="primary"
              size="sm"
              onClick={() => setIsAddUserModalOpen(true)}
            >
              <Plus className="h-3.5 w-3.5" />
              <span>Add New User</span>
            </Button>
          </div>
        </CardHeader>

        {/* User Table */}
        <div className="overflow-x-auto rounded-input border border-line dark:border-dark-line">
          <table className="w-full text-left text-body">
            <thead className="border-b border-line bg-page/60 text-caption font-semibold uppercase text-muted dark:border-dark-line dark:bg-dark-page/60 dark:text-dark-muted">
              <tr>
                <th className="px-4 py-3">Full Name</th>
                <th className="px-4 py-3">Username / USN</th>
                <th className="px-4 py-3">Email Address</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Affiliation / Dept</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line dark:divide-dark-line">
              {filteredUsers.map((user) => (
                <tr
                  key={user.id}
                  className="transition hover:bg-page/40 dark:hover:bg-dark-page/40"
                >
                  <td className="px-4 py-3 font-semibold text-ink dark:text-dark-text">
                    {user.name}
                  </td>
                  <td className="px-4 py-3 font-mono text-caption text-muted dark:text-dark-muted">
                    {user.usn || user.username}
                  </td>
                  <td className="px-4 py-3 text-caption text-ink dark:text-dark-text">
                    {user.email}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-block rounded-pill px-2.5 py-0.5 text-caption font-semibold uppercase tracking-wider ${
                        user.role === 'admin'
                          ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300'
                          : user.role === 'teacher'
                          ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
                          : user.role === 'student'
                          ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300'
                          : 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300'
                      }`}
                    >
                      {user.role}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-caption text-muted dark:text-dark-muted">
                    {user.department || user.studentUsn || 'CSE Department'}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center gap-1.5 rounded-pill px-2 py-0.5 text-[11px] font-semibold ${
                        user.active
                          ? 'bg-risk-low/10 text-risk-low'
                          : 'bg-risk-high/10 text-risk-high'
                      }`}
                    >
                      <span
                        className={`h-1.5 w-1.5 rounded-full ${
                          user.active ? 'bg-risk-low' : 'bg-risk-high'
                        }`}
                      />
                      {user.active ? 'Active' : 'Disabled'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => toggleUserActive(user.id)}
                      className="text-caption font-medium text-accent hover:underline"
                    >
                      {user.active ? 'Deactivate' : 'Activate'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Class Sections & Mentor Allocation Card */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>Academic Sections & Class Cohorts</CardTitle>
              <CardDescription>
                5th Semester Computer Science and Engineering (2024-2025)
              </CardDescription>
            </div>
          </CardHeader>
          <div className="space-y-3">
            {CLASSES.map((cls) => (
              <div
                key={cls.id}
                className="flex items-center justify-between rounded-input border border-line bg-page/30 p-3.5 dark:border-dark-line dark:bg-dark-surface/40"
              >
                <div>
                  <h4 className="font-semibold text-ink dark:text-dark-text">
                    {cls.name} &bull; Section {cls.section}
                  </h4>
                  <p className="text-caption text-muted dark:text-dark-muted">
                    Academic Year: {cls.academicYear} &bull; Total Enrolled: <b>{cls.totalStudents} students</b>
                  </p>
                </div>
                <div className="text-right">
                  <span className="rounded-pill bg-accent/10 px-2.5 py-1 text-caption font-semibold text-accent">
                    {cls.section === 'A' ? 'Mentor: Prof. Anita Rao' : 'Mentor: Prof. Karthik Nair'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* System Activity & Inference Audit Log */}
        <Card>
          <CardHeader>
            <div>
              <CardTitle>Audit Trail & Inference Events</CardTitle>
              <CardDescription>
                System triggers, batch predictions, and parent notification alerts.
              </CardDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => toast.success('Audit trail log exported (camps_audit_log.csv).')}
            >
              <Download className="h-3.5 w-3.5" />
              <span>Export Log</span>
            </Button>
          </CardHeader>
          <div className="space-y-3">
            <div className="flex items-start gap-3 rounded-input border border-line bg-page/30 p-3 text-caption dark:border-dark-line dark:bg-dark-surface/30">
              <span className="mt-0.5 flex h-6 w-6 items-center justify-center rounded-full bg-risk-low/10 text-risk-low">
                <CheckCircle2 className="h-3.5 w-3.5" />
              </span>
              <div>
                <p className="font-semibold text-ink dark:text-dark-text">Batch Prediction Recalculation Completed</p>
                <p className="text-muted dark:text-dark-muted">
                  60 students evaluated using XGBoost v1.0.0; TreeSHAP feature matrices persisted.
                </p>
                <p className="text-[10px] text-muted">Today at 09:30 AM &bull; Automated Cron</p>
              </div>
            </div>

            <div className="flex items-start gap-3 rounded-input border border-line bg-page/30 p-3 text-caption dark:border-dark-line dark:bg-dark-surface/30">
              <span className="mt-0.5 flex h-6 w-6 items-center justify-center rounded-full bg-risk-high/10 text-risk-high">
                <AlertCircle className="h-3.5 w-3.5" />
              </span>
              <div>
                <p className="font-semibold text-ink dark:text-dark-text">High-Risk Parent Email Dispatched</p>
                <p className="text-muted dark:text-dark-muted">
                  Attendance threshold breach (&lt;75%) alert emailed to parent of Rohan Verma (4PM21CS001).
                </p>
                <p className="text-[10px] text-muted">Yesterday at 04:15 PM &bull; Nodemailer Service</p>
              </div>
            </div>

            <div className="flex items-start gap-3 rounded-input border border-line bg-page/30 p-3 text-caption dark:border-dark-line dark:bg-dark-surface/30">
              <span className="mt-0.5 flex h-6 w-6 items-center justify-center rounded-full bg-accent/10 text-accent">
                <FileText className="h-3.5 w-3.5" />
              </span>
              <div>
                <p className="font-semibold text-ink dark:text-dark-text">Mentor Remark Logged</p>
                <p className="text-muted dark:text-dark-muted">
                  Prof. Anita Rao added intervention notes and scheduled Saturday tutorial.
                </p>
                <p className="text-[10px] text-muted">28 Oct 2024 at 11:20 AM &bull; Web App</p>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Retrain Model Modal */}
      <Modal
        isOpen={isRetrainModalOpen}
        onClose={() => !isRetraining && setIsRetrainModalOpen(false)}
        title="Retrain XGBoost Risk Classification Pipeline"
      >
        <div className="space-y-4">
          <p className="text-caption text-muted dark:text-dark-muted">
            Configure hyperparameters and initiate stratified 5-fold cross-validation with SMOTE balance resampling.
          </p>

          <div className="space-y-3">
            <div>
              <label className="text-caption font-semibold text-ink dark:text-dark-text">
                Number of Estimators (Trees): {hyperparams.nEstimators}
              </label>
              <input
                type="range"
                min="50"
                max="300"
                step="10"
                value={hyperparams.nEstimators}
                onChange={(e) =>
                  setHyperparams({ ...hyperparams, nEstimators: Number(e.target.value) })
                }
                className="w-full accent-accent"
                disabled={isRetraining}
              />
            </div>

            <div>
              <label className="text-caption font-semibold text-ink dark:text-dark-text">
                Max Tree Depth: {hyperparams.maxDepth}
              </label>
              <input
                type="range"
                min="3"
                max="10"
                value={hyperparams.maxDepth}
                onChange={(e) =>
                  setHyperparams({ ...hyperparams, maxDepth: Number(e.target.value) })
                }
                className="w-full accent-accent"
                disabled={isRetraining}
              />
            </div>

            <div>
              <label className="text-caption font-semibold text-ink dark:text-dark-text">
                Learning Rate (&eta;): {hyperparams.learningRate}
              </label>
              <input
                type="range"
                min="0.01"
                max="0.3"
                step="0.01"
                value={hyperparams.learningRate}
                onChange={(e) =>
                  setHyperparams({ ...hyperparams, learningRate: Number(e.target.value) })
                }
                className="w-full accent-accent"
                disabled={isRetraining}
              />
            </div>

            <div className="flex items-center justify-between rounded-input border border-line bg-page p-3 dark:border-dark-line dark:bg-dark-page">
              <div>
                <p className="text-caption font-semibold text-ink dark:text-dark-text">
                  SMOTE Class Resampling
                </p>
                <p className="text-[11px] text-muted">Applied strictly on training folds to prevent data leakage.</p>
              </div>
              <input
                type="checkbox"
                checked={hyperparams.smoteEnabled}
                onChange={(e) =>
                  setHyperparams({ ...hyperparams, smoteEnabled: e.target.checked })
                }
                className="h-4 w-4 accent-accent"
                disabled={isRetraining}
              />
            </div>
          </div>

          {/* Progress bar during training */}
          {isRetraining && (
            <div className="space-y-1.5 pt-2">
              <div className="flex justify-between text-caption font-semibold text-accent">
                <span>Optimizing XGBoost objective & computing TreeSHAP...</span>
                <span>{retrainProgress}%</span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-line dark:bg-dark-line">
                <div
                  className="h-full bg-accent transition-all duration-300"
                  style={{ width: `${retrainProgress}%` }}
                />
              </div>
            </div>
          )}

          <div className="mt-5 flex justify-end gap-2 border-t border-line pt-3 dark:border-dark-line">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsRetrainModalOpen(false)}
              disabled={isRetraining}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={handleStartRetraining}
              isLoading={isRetraining}
            >
              <Sparkles className="h-3.5 w-3.5" />
              <span>Execute Retraining</span>
            </Button>
          </div>
        </div>
      </Modal>

      {/* Add New User Modal */}
      <Modal
        isOpen={isAddUserModalOpen}
        onClose={() => setIsAddUserModalOpen(false)}
        title="Register New Institutional User"
      >
        <form onSubmit={handleAddUser} className="space-y-3.5">
          <Input
            label="Full Name"
            placeholder="e.g. Dr. Sunil Kumar"
            value={newUser.name}
            onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
            required
          />

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Username"
              placeholder="e.g. sunil.kumar"
              value={newUser.username}
              onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
              required
            />
            <Input
              label="Email Address"
              type="email"
              placeholder="e.g. sunil.kumar@pesitm.edu"
              value={newUser.email}
              onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Select
              label="Assigned Role"
              value={newUser.role}
              onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
              options={[
                { value: 'admin', label: 'Administrator' },
                { value: 'teacher', label: 'Faculty / Mentor' },
                { value: 'student', label: 'Student' },
                { value: 'parent', label: 'Parent / Guardian' },
              ]}
            />
            <Input
              label={newUser.role === 'student' ? 'USN (University Seat Number)' : 'Department'}
              placeholder={newUser.role === 'student' ? '4PM21CS065' : 'CSE Department'}
              value={newUser.role === 'student' ? newUser.usn : newUser.department}
              onChange={(e) =>
                newUser.role === 'student'
                  ? setNewUser({ ...newUser, usn: e.target.value })
                  : setNewUser({ ...newUser, department: e.target.value })
              }
            />
          </div>

          <div className="mt-5 flex justify-end gap-2 border-t border-line pt-3 dark:border-dark-line">
            <Button
              variant="outline"
              size="sm"
              type="button"
              onClick={() => setIsAddUserModalOpen(false)}
            >
              Cancel
            </Button>
            <Button variant="primary" size="sm" type="submit">
              Register User
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
