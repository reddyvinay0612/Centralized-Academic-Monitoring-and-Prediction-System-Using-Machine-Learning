import React from 'react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

export function CieRadarChart({ marks = null, height = 260 }) {
  if (!marks) {
    return (
      <div className="flex h-48 items-center justify-center text-caption text-muted">
        No assessment breakdown available for radar profiling.
      </div>
    );
  }

  // Normalized scores out of 100% for radar polygon
  const data = [
    {
      subject: 'CIE 1 (50)',
      score: marks.cie1 !== undefined ? Math.min(100, Math.round(((parseFloat(marks.cie1) || 0) / 50) * 100)) : 0,
      rawValue: marks.cie1 || 0,
      max: 50,
      benchmark: 70
    },
    {
      subject: 'CIE 2 (50)',
      score: marks.cie2 !== undefined ? Math.min(100, Math.round(((parseFloat(marks.cie2) || 0) / 50) * 100)) : 0,
      rawValue: marks.cie2 || 0,
      max: 50,
      benchmark: 70
    },
    {
      subject: 'CIE 3 (50)',
      score: marks.cie3 !== undefined ? Math.min(100, Math.round(((parseFloat(marks.cie3) || 0) / 50) * 100)) : 0,
      rawValue: marks.cie3 || 0,
      max: 50,
      benchmark: 70
    },
    {
      subject: 'Assignment (10)',
      score: marks.assignment !== undefined || marks.assignment_marks !== undefined ?
        Math.min(100, Math.round(((parseFloat(marks.assignment || marks.assignment_marks) || 0) / 10) * 100)) : 0,
      rawValue: marks.assignment || marks.assignment_marks || 0,
      max: 10,
      benchmark: 80
    },
    {
      subject: 'Quiz (10)',
      score: marks.quiz !== undefined || marks.quiz_marks !== undefined ?
        Math.min(100, Math.round(((parseFloat(marks.quiz || marks.quiz_marks) || 0) / 10) * 100)) : 0,
      rawValue: marks.quiz || marks.quiz_marks || 0,
      max: 10,
      benchmark: 80
    }
  ];

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="rounded-lg border border-line bg-surface p-2.5 shadow-md dark:border-dark-line dark:bg-dark-surface text-caption">
          <p className="font-heading font-bold text-ink dark:text-dark-text mb-1">{item.subject}</p>
          <p className="text-accent font-semibold">
            Raw Score: <span className="font-bold">{item.rawValue}</span> / {item.max}
          </p>
          <p className="text-muted">
            Performance Index: <span className="font-bold text-ink dark:text-dark-text">{item.score}%</span>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data}>
          <PolarGrid stroke="#d9e1ea" strokeDasharray="3 3" opacity={0.7} />
          <PolarAngleAxis
            dataKey="subject"
            stroke="#5b6b82"
            fontSize={11}
            tickLine={false}
          />
          <PolarRadiusAxis
            angle={30}
            domain={[0, 100]}
            stroke="#5b6b82"
            fontSize={10}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="bottom"
            height={28}
            formatter={(val) => <span className="text-caption font-semibold">{val}</span>}
          />
          <Radar
            name="Student Continuous Score (%)"
            dataKey="score"
            stroke="#2f6bff"
            fill="#2f6bff"
            fillOpacity={0.4}
          />
          <Radar
            name="VTU Benchmark Target (%)"
            dataKey="benchmark"
            stroke="#0f9d8a"
            fill="#0f9d8a"
            fillOpacity={0.1}
            strokeDasharray="4 4"
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default CieRadarChart;
