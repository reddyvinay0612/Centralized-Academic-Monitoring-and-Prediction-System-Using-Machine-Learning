import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { Mail, ArrowRight, CheckCircle2, KeyRound } from 'lucide-react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import api from '@/services/api';

export default function ForgotPasswordModal({ isOpen, onClose }) {
  const [identifier, setIdentifier] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [devToken, setDevToken] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!identifier.trim()) {
      toast.error('Please enter your registered email, USN, or mobile number.');
      return;
    }

    setIsLoading(true);
    try {
      const res = await api.post('/auth/forgot-password', { identifier });
      setIsLoading(false);
      setSubmitted(true);
      if (res.data?.dev_reset_token) {
        setDevToken(res.data.dev_reset_token);
      }
      toast.success('Password reset instructions dispatched.');
    } catch (err) {
      setIsLoading(false);
      setSubmitted(true);
      toast.success('Password reset instructions dispatched.');
    }
  };

  const handleResetState = () => {
    setSubmitted(false);
    setDevToken(null);
    setIdentifier('');
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleResetState} title="Reset Account Password">
      {submitted ? (
        <div className="space-y-4 text-center py-2">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-risk-low/10 text-risk-low">
            <CheckCircle2 className="h-6 w-6" />
          </div>
          <h4 className="font-heading text-heading font-semibold text-ink dark:text-dark-text">
            Instructions Dispatched
          </h4>
          <p className="text-caption text-muted dark:text-dark-muted">
            If an active account is registered with <span className="font-semibold text-ink dark:text-dark-text">{identifier}</span>, password reset instructions and a single-use verification link have been sent.
          </p>

          {devToken && (
            <div className="rounded-input border border-line bg-page p-3 text-left font-mono text-[11px] text-accent dark:border-dark-line dark:bg-dark-page break-all">
              <span className="font-semibold text-muted">Dev Reset Token: </span>
              {devToken}
            </div>
          )}

          <div className="pt-2">
            <Button variant="primary" size="sm" onClick={handleResetState} className="w-full">
              Back to Login
            </Button>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <p className="text-caption text-muted dark:text-dark-muted leading-relaxed">
            Enter your registered Email address, University Seat Number (USN), or Employee ID. A single-use cryptographic recovery link valid for 60 minutes will be generated.
          </p>

          <div>
            <label className="mb-1 block text-caption font-medium text-ink dark:text-dark-text">
              Identifier (Email / USN / Phone)
            </label>
            <div className="relative">
              <KeyRound className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
              <input
                type="text"
                required
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder="e.g. 4PM21CS001 or parent@gmail.com"
                className="w-full rounded-input border border-line bg-surface py-2 pl-9 pr-3 text-body text-ink focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
              />
            </div>
          </div>

          <div className="flex justify-end gap-2 border-t border-line pt-3 dark:border-dark-line">
            <Button variant="outline" size="sm" type="button" onClick={handleResetState}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" type="submit" isLoading={isLoading}>
              <span>Send Reset Instructions</span>
              <ArrowRight className="h-4 w-4" />
            </Button>
          </div>
        </form>
      )}
    </Modal>
  );
}
