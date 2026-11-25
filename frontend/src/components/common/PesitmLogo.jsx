import React from 'react';

/**
 * Authentic PES Institute of Technology & Management (PESITM) Compass Emblem Logo.
 * Matches official PES Trust star emblem: 8-point compass star with red & navy points and central globe.
 */
export default function PesitmLogo({ className = 'h-14 w-14', size = 56 }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 100 100"
      width={size}
      height={size}
      className={`shrink-0 ${className}`}
      aria-label="PESITM Emblem"
    >
      <defs>
        <radialGradient id="pesGlobeGrad" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#38bdf8" />
          <stop offset="70%" stopColor="#0284c7" />
          <stop offset="100%" stopColor="#0369a1" />
        </radialGradient>
        <linearGradient id="pesGoldRing" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#f59e0b" />
          <stop offset="100%" stopColor="#d97706" />
        </linearGradient>
      </defs>

      {/* Outer Ring */}
      <circle cx="50" cy="50" r="32" fill="none" stroke="url(#pesGoldRing)" strokeWidth="2.5" />

      {/* 4 Secondary Navy Points (NE, NW, SE, SW) */}
      <polygon points="50,50 68,32 50,42" fill="#1e3a8a" />
      <polygon points="50,50 68,32 58,50" fill="#0f172a" />

      <polygon points="50,50 32,32 50,42" fill="#1e3a8a" />
      <polygon points="50,50 32,32 42,50" fill="#0f172a" />

      <polygon points="50,50 32,68 42,50" fill="#1e3a8a" />
      <polygon points="50,50 32,68 50,58" fill="#0f172a" />

      <polygon points="50,50 68,68 58,50" fill="#1e3a8a" />
      <polygon points="50,50 68,68 50,58" fill="#0f172a" />

      {/* 4 Primary Red Points (N, S, E, W) */}
      {/* North Point */}
      <polygon points="50,50 50,2 45,45" fill="#ef4444" />
      <polygon points="50,50 50,2 55,45" fill="#dc2626" />

      {/* South Point */}
      <polygon points="50,50 50,98 45,55" fill="#ef4444" />
      <polygon points="50,50 50,98 55,55" fill="#b91c1c" />

      {/* East Point */}
      <polygon points="50,50 98,50 55,45" fill="#ef4444" />
      <polygon points="50,50 98,50 55,55" fill="#b91c1c" />

      {/* West Point */}
      <polygon points="50,50 2,50 45,45" fill="#ef4444" />
      <polygon points="50,50 2,50 45,55" fill="#dc2626" />

      {/* Center Globe */}
      <circle cx="50" cy="50" r="16" fill="url(#pesGlobeGrad)" stroke="#ffffff" strokeWidth="1.5" />

      {/* Globe Meridian & Equator Lines */}
      <ellipse cx="50" cy="50" rx="15" ry="6" fill="none" stroke="#ffffff" strokeWidth="0.8" opacity="0.8" />
      <ellipse cx="50" cy="50" rx="7" ry="15" fill="none" stroke="#ffffff" strokeWidth="0.8" opacity="0.8" />
      <line x1="34" y1="50" x2="66" y2="50" stroke="#ffffff" strokeWidth="0.8" opacity="0.8" />
      <line x1="50" y1="34" x2="50" y2="66" stroke="#ffffff" strokeWidth="0.8" opacity="0.8" />

      {/* Central Star Point / PES Emblem Text */}
      <text
        x="50"
        y="53.5"
        textAnchor="middle"
        fontSize="7.5"
        fontWeight="900"
        fill="#ffffff"
        fontFamily="sans-serif"
        letterSpacing="0.5"
      >
        PES
      </text>
    </svg>
  );
}
