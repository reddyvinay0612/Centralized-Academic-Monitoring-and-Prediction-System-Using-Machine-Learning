import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  AlertTriangle,
  Mail,
  Phone,
  CheckCircle2,
  Clock,
  Filter,
  ArrowRight,
  ExternalLink,
  Send,
  RefreshCw,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Pill } from '@/components/ui/Pill';
import { INITIAL_ALERTS } from '@/mocks/data';
import { formatDate } from '@/utils/format';

export default function Alerts() {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState(INITIAL_ALERTS);
  const [activeTab, setActiveTab] = useState('open'); // 'open' | 'contacted'

  const openAlerts = alerts.filter((a) => a.status === 'open');
  const contactedAlerts = alerts.filter((a) => a.status === 'contacted');

  const displayedAlerts = activeTab === 'open' ? openAlerts : contactedAlerts;

  // Mark an alert as contacted
  const handleMarkContacted = (id) => {
    setAlerts((prev) =>
      prev.map((a) => {
        if (a.id === id) {
          toast.success(`Alert for ${a.studentName} marked as contacted.`);
          return { ...a, status: 'contacted' };
        }
        return a;
      })
    );
  };

  // Resend email notification
  const handleResendEmail = (studentName) => {
    toast.success(`Parent notification email queued for ${studentName} via Nodemailer service.`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-input bg-risk-high/10 text-risk-high">
              <AlertTriangle className="h-4 w-4" />
            </span>
            <h1 className="font-heading text-display font-bold text-ink dark:text-dark-text">
              Early-Warning Alerts & Intervention Triggers
            </h1>
          </div>
          <p className="mt-1 text-body text-muted dark:text-dark-muted">
            PESITM automated alerting pipeline &bull; Triggers on attendance &lt; 75% or predicted failure probability &ge; 60%.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            toast.success('Running real-time threshold scan across 60 student profiles...');
          }}
        >
          <RefreshCw className="h-3.5 w-3.5" />
          <span>Re-scan Thresholds</span>
        </Button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-line dark:border-dark-line">
        <button
          onClick={() => setActiveTab('open')}
          className={`flex items-center gap-2 border-b-2 px-4 py-2.5 font-heading text-caption font-semibold transition ${
            activeTab === 'open'
              ? 'border-accent text-accent'
              : 'border-transparent text-muted hover:text-ink dark:text-dark-muted dark:hover:text-dark-text'
          }`}
        >
          <span>Open Alerts</span>
          <span className="rounded-full bg-risk-high/10 px-2 py-0.5 text-[11px] font-bold text-risk-high">
            {openAlerts.length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab('contacted')}
          className={`flex items-center gap-2 border-b-2 px-4 py-2.5 font-heading text-caption font-semibold transition ${
            activeTab === 'contacted'
              ? 'border-accent text-accent'
              : 'border-transparent text-muted hover:text-ink dark:text-dark-muted dark:hover:text-dark-text'
          }`}
        >
          <span>Resolved / Contacted</span>
          <span className="rounded-full bg-line px-2 py-0.5 text-[11px] font-medium text-muted dark:bg-dark-line">
            {contactedAlerts.length}
          </span>
        </button>
      </div>

      {/* Alerts Grid */}
      <div className="space-y-4">
        {displayedAlerts.length === 0 ? (
          <Card className="py-12 text-center text-muted">
            <CheckCircle2 className="mx-auto h-8 w-8 text-risk-low" />
            <p className="mt-2 text-body font-semibold text-ink dark:text-dark-text">
              No alerts in this category
            </p>
            <p className="text-caption text-muted">
              All flagged student interventions have been addressed.
            </p>
          </Card>
        ) : (
          displayedAlerts.map((alert) => (
            <Card
              key={alert.id}
              className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center"
            >
              <div className="space-y-2">
                <div className="flex flex-wrap items-center gap-2">
                  <Pill level={alert.riskLevel} />
                  <h3 className="font-heading text-heading font-semibold text-ink dark:text-dark-text">
                    {alert.studentName}
                  </h3>
                  <span className="font-mono text-caption text-muted dark:text-dark-muted">
                    {alert.usn}
                  </span>
                  <span className="text-[11px] text-muted">
                    &bull; Flagged on {formatDate(alert.createdAt)}
                  </span>
                </div>

                <p className="text-caption text-ink dark:text-dark-text">
                  <span className="font-semibold text-risk-high">Reason: </span>
                  {alert.reason}
                </p>

                <div className="flex flex-wrap items-center gap-3 text-[11px] text-muted dark:text-dark-muted">
                  <div className="flex items-center gap-1 text-risk-low">
                    <Mail className="h-3.5 w-3.5" />
                    <span>Parent Notification Email Sent</span>
                  </div>
                  <span>&bull;</span>
                  <span>Probability Score: <b>{Math.round(alert.riskScore * 100)}%</b></span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleResendEmail(alert.studentName)}
                >
                  <Send className="h-3 w-3" />
                  <span>Resend Notice</span>
                </Button>

                {alert.status === 'open' ? (
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleMarkContacted(alert.id)}
                  >
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    <span>Mark Contacted</span>
                  </Button>
                ) : (
                  <span className="inline-flex items-center gap-1 text-caption font-semibold text-risk-low">
                    <CheckCircle2 className="h-4 w-4" />
                    <span>Contacted</span>
                  </span>
                )}

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate(`/students/${alert.studentId}`)}
                >
                  <span>Dossier</span>
                  <ExternalLink className="h-3 w-3" />
                </Button>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
