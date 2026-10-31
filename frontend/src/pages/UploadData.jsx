import React from 'react';

export default function UploadData() {
  return (
    <div className="p-6">
      <h1 className="font-heading text-display text-ink dark:text-dark-text">Import student data</h1>
      <p className="mt-1 text-body text-muted dark:text-dark-muted">
        Upload class CSV or Excel to validate records and refresh XGBoost predictions.
      </p>
    </div>
  );
}
