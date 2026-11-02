import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { getRiskColor } from '@/utils/risk';

export function RiskDonut({ students = [] }) {
  const lowCount = students.filter((s) => s.riskLevel === 'low').length;
  const medCount = students.filter((s) => s.riskLevel === 'medium').length;
  const highCount = students.filter((s) => s.riskLevel === 'high').length;
  const total = students.length || 1;

  const data = [
    { name: 'Low Risk', value: lowCount, level: 'low', color: '#0f9d8a' },
    { name: 'Medium Risk', value: medCount, level: 'medium', color: '#d89a06' },
    { name: 'High Risk', value: highCount, level: 'high', color: '#d9445a' },
  ];

  const highPct = Math.round((highCount / total) * 100);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      const pct = Math.round((item.value / total) * 100);
      return (
        <div className="rounded-input border border-line bg-surface p-2.5 shadow-card dark:border-dark-line dark:bg-dark-surface">
          <p className="font-heading text-caption font-semibold" style={{ color: item.color }}>
            {item.name}
          </p>
          <p className="text-body font-medium text-ink dark:text-dark-text">
            {item.value} students <span className="text-caption text-muted">({pct}%)</span>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="flex h-full flex-col items-center justify-between">
      <div className="relative h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Tooltip content={<CustomTooltip />} />
            <Pie
              data={data}
              innerRadius={65}
              outerRadius={88}
              paddingAngle={3}
              dataKey="value"
              stroke="transparent"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>

        {/* Center label */}
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="font-heading text-2xl font-bold text-risk-high">{highCount}</span>
          <span className="text-[11px] font-medium uppercase tracking-wider text-muted dark:text-dark-muted">
            High Risk ({highPct}%)
          </span>
        </div>
      </div>

      {/* Legend list */}
      <div className="flex w-full items-center justify-around border-t border-line/60 pt-3 text-caption dark:border-dark-line/60">
        <div className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-risk-low" />
          <span className="text-muted dark:text-dark-muted">Safe ({lowCount})</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-risk-medium" />
          <span className="text-muted dark:text-dark-muted">Moderate ({medCount})</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-risk-high" />
          <span className="font-medium text-risk-high">Critical ({highCount})</span>
        </div>
      </div>
    </div>
  );
}
export default RiskDonut;
