import React from 'react';
import { Pill } from '@/components/ui/Pill';
import { getRiskLevel, formatRiskScore, getRiskColor } from '@/utils/risk';

export function RiskGauge({ score = 0, size = 180 }) {
  const level = getRiskLevel(score);
  const color = getRiskColor(level);
  const pct = Math.min(100, Math.max(0, Math.round(score * 100)));

  // SVG Gauge calculations (semi-circle from 180 to 0 degrees)
  // Radius 70, stroke 14, circumference for half circle = PI * 70 = ~220
  const radius = 64;
  const strokeWidth = 12;
  const cx = 90;
  const cy = 80;
  const halfCircumference = Math.PI * radius; // ~201
  const strokeDashoffset = halfCircumference - (pct / 100) * halfCircumference;

  const getDiagnosticSentence = () => {
    if (level === 'high') {
      return 'Immediate faculty intervention needed: high probability of falling into academic detention or semester drop.';
    }
    if (level === 'medium') {
      return 'Moderate risk detected: borderline attendance or internal assessment dips require monitoring.';
    }
    return 'Optimal academic trajectory: student is well above VTU credit minimums with consistent attendance.';
  };

  return (
    <div className="flex flex-col items-center text-center">
      <div className="relative" style={{ width: size, height: size * 0.62 }}>
        <svg
          viewBox="0 0 180 100"
          className="w-full h-full overflow-visible"
        >
          {/* Background Arc */}
          <path
            d="M 26 80 A 64 64 0 0 1 154 80"
            fill="none"
            stroke="#d9e1ea"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            className="dark:stroke-dark-line"
          />

          {/* Value Arc */}
          <path
            d="M 26 80 A 64 64 0 0 1 154 80"
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={halfCircumference}
            strokeDashoffset={strokeDashoffset}
            style={{
              transition: 'stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
            }}
          />

          {/* Needle Center Pin */}
          <circle cx={cx} cy={cy} r="4" fill="#14213d" className="dark:fill-dark-text" />
        </svg>

        {/* Center Content */}
        <div className="absolute inset-x-0 bottom-0 flex flex-col items-center">
          <span className="font-heading text-3xl font-bold tracking-tight" style={{ color }}>
            {pct}%
          </span>
          <span className="text-[11px] font-medium uppercase tracking-wider text-muted dark:text-dark-muted">
            Risk Probability
          </span>
        </div>
      </div>

      <div className="mt-3 flex items-center gap-2">
        <Pill level={level} />
      </div>

      <p className="mt-2 text-caption text-muted dark:text-dark-muted max-w-xs">
        {getDiagnosticSentence()}
      </p>
    </div>
  );
}
export default RiskGauge;
