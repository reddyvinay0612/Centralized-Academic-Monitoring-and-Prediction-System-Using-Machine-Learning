import React from 'react';

export function Card({ className = '', children, ...props }) {
  return (
    <div
      className={`rounded-card border border-line bg-surface p-5 shadow-subtle transition-shadow duration-150 dark:border-dark-line dark:bg-dark-surface ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ className = '', children, ...props }) {
  return (
    <div className={`mb-4 flex items-center justify-between gap-3 ${className}`} {...props}>
      {children}
    </div>
  );
}

export function CardTitle({ className = '', children, ...props }) {
  return (
    <h3
      className={`font-heading text-heading font-semibold text-ink dark:text-dark-text ${className}`}
      {...props}
    >
      {children}
    </h3>
  );
}

export function CardDescription({ className = '', children, ...props }) {
  return (
    <p className={`mt-0.5 text-caption text-muted dark:text-dark-muted ${className}`} {...props}>
      {children}
    </p>
  );
}
