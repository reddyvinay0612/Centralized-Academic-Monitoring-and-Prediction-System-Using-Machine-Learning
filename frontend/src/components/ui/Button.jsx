import React from 'react';

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled = false,
  className = '',
  ...props
}) {
  const baseClasses =
    'inline-flex items-center justify-center font-medium rounded-input transition-colors duration-150 focus-visible:outline-none disabled:opacity-50 disabled:pointer-events-none active:scale-[0.99]';

  const variants = {
    primary: 'bg-accent text-white hover:bg-accent-hover shadow-subtle',
    secondary: 'bg-page text-ink hover:bg-line/70 dark:bg-dark-page dark:text-dark-text dark:hover:bg-dark-line',
    outline: 'border border-line text-ink hover:bg-page dark:border-dark-line dark:text-dark-text dark:hover:bg-dark-surface',
    danger: 'bg-risk-high text-white hover:bg-risk-high/90 shadow-subtle',
    ghost: 'text-muted hover:text-ink hover:bg-page dark:text-dark-muted dark:hover:text-dark-text dark:hover:bg-dark-surface',
  };

  const sizes = {
    sm: 'text-caption px-3 py-1.5 gap-1.5',
    md: 'text-body px-4 py-2 gap-2',
    lg: 'text-heading px-5 py-2.5 gap-2.5',
  };

  return (
    <button
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <>
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
          <span>Processing...</span>
        </>
      ) : (
        children
      )}
    </button>
  );
}
