import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getRiskColor, formatRiskScore, getRiskLabel } from '@/utils/risk';

/**
 * Signature Element: <RiskStrip />
 * One thin bar per student, sorted by predicted risk probability.
 * Interactive hover with accessible tooltip (name + USN + %) and click-to-profile navigation.
 */
export function RiskStrip({ students = [], onSelectStudent }) {
  const navigate = useNavigate();
  const [hovered, setHovered] = useState(null);

  // Sort students from lowest risk to highest risk
  const sortedStudents = [...students].sort((a, b) => (a.riskScore || 0) - (b.riskScore || 0));

  const lowCount = students.filter((s) => s.riskLevel === 'low').length;
  const medCount = students.filter((s) => s.riskLevel === 'medium').length;
  const highCount = students.filter((s) => s.riskLevel === 'high').length;

  return (
    <div className="w-full">
      {/* Legend & Summary Counts Header */}
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2 text-caption text-muted dark:text-dark-muted">
        <div className="flex items-center gap-1.5 font-medium text-ink dark:text-dark-text">
          <span>Risk spectrum</span>
          <span className="text-muted dark:text-dark-muted">({students.length} students sorted)</span>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-risk-low" />
            <span>Low ({lowCount})</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-risk-medium" />
            <span>Medium ({medCount})</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-risk-high" />
            <span className="font-semibold text-risk-high">High ({highCount})</span>
          </div>
        </div>
      </div>

      {/* The Visual Strip */}
      <div
        className="relative flex h-14 w-full items-end gap-[2px] rounded-card border border-line bg-surface p-2 shadow-subtle dark:border-dark-line dark:bg-dark-surface"
        role="region"
        aria-label="Student Risk Spectrum"
      >
        {sortedStudents.map((student) => {
          const color = getRiskColor(student.riskLevel);
          const heightPct = Math.max(25, Math.round((student.riskScore || 0.1) * 100));
          const isCurrent = hovered?.id === student.id;

          return (
            <button
              key={student.id}
              onClick={() => {
                if (onSelectStudent) onSelectStudent(student);
                else navigate(`/students/${student.id}`);
              }}
              onMouseEnter={() => setHovered(student)}
              onMouseLeave={() => setHovered(null)}
              onFocus={() => setHovered(student)}
              onBlur={() => setHovered(null)}
              className="relative flex-1 rounded-t-sm transition-all duration-100 hover:z-10 focus-visible:outline-none"
              style={{
                height: `${heightPct}%`,
                backgroundColor: color,
                opacity: hovered && !isCurrent ? 0.45 : 1,
                transform: isCurrent ? 'scaleY(1.15) scaleX(1.3)' : 'none',
              }}
              aria-label={`${student.name} (${student.usn}): ${formatRiskScore(student.riskScore)} ${getRiskLabel(student.riskLevel)}`}
            />
          );
        })}

        {/* Hover Tooltip Overlay */}
        {hovered && (
          <div
            className="pointer-events-none absolute -top-12 left-1/2 z-30 -translate-x-1/2 rounded-input border border-line bg-ink px-3 py-1.5 text-caption font-medium text-white shadow-card transition-all dark:border-dark-line"
            style={{ minWidth: '180px', textAlign: 'center' }}
          >
            <div className="font-semibold">{hovered.name}</div>
            <div className="text-[11px] opacity-80">
              {hovered.usn} &bull; Risk: <b>{formatRiskScore(hovered.riskScore)}</b> ({getRiskLabel(hovered.riskLevel)})
            </div>
          </div>
        )}
      </div>

      <div className="mt-1 flex justify-between px-1 text-[11px] text-muted dark:text-dark-muted">
        <span>&larr; Safe / Low Risk</span>
        <span>Critical Attention &rarr;</span>
      </div>
    </div>
  );
}
