import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
} from 'recharts';

export function AttendanceBar({ subjects = [], height = 230 }) {
  if (!subjects || subjects.length === 0) {
    return (
      <div className="flex h-48 items-center justify-center text-caption text-muted">
        No subject attendance logs available.
      </div>
    );
  }

  const data = subjects.map((s) => ({
    subject: s.subject || s.subject_name || s.subject_code || 'Subject',
    percentage: Number(s.percentage || 0),
    color: Number(s.percentage || 0) >= 75 ? '#0f9d8a' : '#d9445a',
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      const isShortage = item.percentage < 75;
      return (
        <div className="rounded-input border border-line bg-surface p-2.5 shadow-card dark:border-dark-line dark:bg-dark-surface">
          <p className="font-heading text-caption font-semibold text-ink dark:text-dark-text">{item.subject}</p>
          <p className="text-body font-medium" style={{ color: item.color }}>
            Attendance: <span className="font-bold">{item.percentage}%</span>
          </p>
          {isShortage && (
            <p className="mt-1 text-[11px] font-semibold text-risk-high">
              &bull; Below VTU 75% minimum (condonation required)
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 10, right: 30, left: 10, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#d9e1ea" horizontal={false} opacity={0.6} />
          <XAxis
            type="number"
            domain={[0, 100]}
            ticks={[0, 25, 50, 75, 100]}
            stroke="#5b6b82"
            fontSize={11}
            unit="%"
          />
          <YAxis
            type="category"
            dataKey="subject"
            stroke="#5b6b82"
            fontSize={12}
            width={130}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine
            x={75}
            stroke="#d9445a"
            strokeDasharray="4 4"
            strokeWidth={1.5}
            label={{
              value: 'VTU 75%',
              position: 'insideTopRight',
              fill: '#d9445a',
              fontSize: 10,
              fontWeight: 600,
            }}
          />
          <Bar dataKey="percentage" radius={[0, 4, 4, 0]} barSize={16}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
export default AttendanceBar;
