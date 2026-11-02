import React, { useEffect } from 'react';

export function Modal({ isOpen, onClose, title, children, maxWidth = 'max-w-lg' }) {
  useEffect(() => {
    function handleKeyDown(e) {
      if (e.key === 'Escape') onClose();
    }
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-ink/40 backdrop-blur-sm transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal Dialog Content */}
      <div
        className={`relative w-full ${maxWidth} rounded-card border border-line bg-surface p-6 shadow-card transition-all dark:border-dark-line dark:bg-dark-surface`}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <div className="flex items-center justify-between pb-3 border-b border-line dark:border-dark-line">
          <h3 id="modal-title" className="font-heading text-heading text-ink dark:text-dark-text">
            {title}
          </h3>
          <button
            onClick={onClose}
            className="rounded-input p-1 text-muted transition hover:bg-page hover:text-ink dark:text-dark-muted dark:hover:bg-dark-page dark:hover:text-dark-text"
            aria-label="Close modal"
          >
            &times;
          </button>
        </div>

        <div className="mt-4">{children}</div>
      </div>
    </div>
  );
}
