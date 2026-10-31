import React from 'react';
import { useParams } from 'react-router-dom';

export default function StudentProfile() {
  const { id } = useParams();

  return (
    <div className="p-6">
      <h1 className="font-heading text-display text-ink dark:text-dark-text">Student diagnostic profile</h1>
      <p className="mt-1 text-body text-muted dark:text-dark-muted">
        Viewing academic metrics and TreeSHAP explainability for Student ID #{id}.
      </p>
    </div>
  );
}
