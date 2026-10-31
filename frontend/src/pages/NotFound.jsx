import React from 'react';
import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-page p-4 text-center dark:bg-dark-page">
      <span className="font-heading text-[64px] font-bold text-accent">404</span>
      <h1 className="mt-2 font-heading text-display text-ink dark:text-dark-text">Page not found</h1>
      <p className="mt-2 max-w-md text-body text-muted dark:text-dark-muted">
        The requested URL was not found. Please verify the web address or return to your overview.
      </p>
      <Link
        to="/overview"
        className="mt-6 inline-flex items-center rounded-input bg-accent px-5 py-2.5 font-medium text-white transition hover:bg-accent-hover focus-visible:outline-none"
      >
        Return to overview
      </Link>
    </div>
  );
}
