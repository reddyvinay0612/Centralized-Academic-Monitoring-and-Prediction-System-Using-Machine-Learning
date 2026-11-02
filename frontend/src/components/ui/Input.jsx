import React from 'react';

export function Input({ label, error, helperText, className = '', id, ...props }) {
  const inputId = id || props.name || Math.random().toString(36).substring(7);

  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={inputId}
          className="mb-1.5 block text-caption font-medium text-ink dark:text-dark-text"
        >
          {label}
        </label>
      )}
      <input
        id={inputId}
        className={`w-full rounded-input border bg-surface px-3.5 py-2 text-body text-ink transition duration-150 placeholder:text-muted/60 focus:border-accent focus-visible:outline-none dark:border-dark-line dark:bg-dark-surface dark:text-dark-text ${
          error ? 'border-risk-high focus:border-risk-high' : 'border-line'
        } ${className}`}
        {...props}
      />
      {error ? (
        <p className="mt-1 text-caption text-risk-high">{error}</p>
      ) : helperText ? (
        <p className="mt-1 text-caption text-muted dark:text-dark-muted">{helperText}</p>
      ) : null}
    </div>
  );
}

export function Select({ label, error, options = [], className = '', id, ...props }) {
  const selectId = id || props.name || Math.random().toString(36).substring(7);

  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={selectId}
          className="mb-1.5 block text-caption font-medium text-ink dark:text-dark-text"
        >
          {label}
        </label>
      )}
      <select
        id={selectId}
        className={`w-full rounded-input border bg-surface px-3 py-2 text-body text-ink transition duration-150 focus:border-accent focus-visible:outline-none dark:border-dark-line dark:bg-dark-surface dark:text-dark-text ${
          error ? 'border-risk-high' : 'border-line'
        } ${className}`}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && <p className="mt-1 text-caption text-risk-high">{error}</p>}
    </div>
  );
}
