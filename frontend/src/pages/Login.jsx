import React from 'react';

export default function Login() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-page p-4 dark:bg-dark-page">
      <div className="w-full max-w-md rounded-card border border-line bg-surface p-8 shadow-card dark:border-dark-line dark:bg-dark-surface">
        <h1 className="font-heading text-display text-ink dark:text-dark-text">Sign in</h1>
        <p className="mt-2 text-body text-muted dark:text-dark-muted">
          Centralized Academic Monitoring and Prediction System
        </p>
        <div className="mt-6 rounded-input bg-page p-4 text-caption text-muted dark:bg-dark-page dark:text-dark-muted">
          Routing skeleton active. Full login form and mock auth arriving in Phase 2.
        </div>
      </div>
    </div>
  );
}
