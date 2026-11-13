import React from 'react';
import { getRiskBadgeClasses, getRiskLabel } from '@/utils/risk';

export function Pill({ level, label, variant = 'risk', className = '', children }) {
  const textLabel = label || children || (variant === 'risk' ? getRiskLabel(level) : '');

  if (variant === 'risk') {
    const badgeStyle = getRiskBadgeClasses(level);

    return (
      <span
        className={`inline-flex items-center gap-1.5 rounded-pill px-2.5 py-0.5 text-caption font-medium tracking-tight ${badgeStyle} ${className}`}
      >
        <span
          className="h-1.5 w-1.5 rounded-full"
          style={{
            backgroundColor:
              level === 'high' ? '#d9445a' : level === 'medium' ? '#d89a06' : '#0f9d8a',
          }}
          aria-hidden="true"
        />
        {textLabel}
      </span>
    );
  }

  return (
    <span
      className={`inline-flex items-center rounded-pill bg-page px-2.5 py-0.5 text-caption font-medium text-muted dark:bg-dark-page dark:text-dark-muted ${className}`}
    >
      {textLabel}
    </span>
  );
}
