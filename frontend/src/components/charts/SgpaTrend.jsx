import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

export function SgpaTrend({
  history = [7.12, 7.28, 7.35, 7.48, 7.55],
  targetGpa = 7.0,
  showBenchmark = true,
  height = 220,
}) {
  const chartData = history.map((val, idx) => ({
    semester: `Sem ${idx + 1}`,
    gpa: Number(val),
  }));

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="rounded-input border border-line bg-surface p-2.5 shadow-card dark:border-dark-line dark:bg-dark-surface">
          <p className="font-heading text-caption font-semibold text-ink dark:text-dark-text">{label}</p>
          <p className="text-body font-medium text-accent">
            SGPA: <span className="font-bold">{payload[0].value.toFixed(2)}</span> / 10.0
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="sgpaGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#2f6bff" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#2f6bff" stopOpacity={0.0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#d9e1ea" vertical={false} opacity={0.6} />
          <XAxis
            dataKey="semester"
            stroke="#5b6b82"
            fontSize={12}
            tickLine={false}
            axisLine={{ stroke: '#d9e1ea' }}
          />
          <YAxis
            domain={[4.0, 10.0]}
            ticks={[4.0, 6.0, 7.0, 8.0, 10.0]}
            stroke="#5b6b82"
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          {showBenchmark && (
            <ReferenceLine
              y={targetGpa}
              stroke="#0f9d8a"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              label={{
                value: 'VTU First Class (7.0)',
                position: 'insideBottomRight',
                fill: '#0f9d8a',
                fontSize: 11,
              }}
            />
          )}
          <Area
            type="monotone"
            dataKey="gpa"
            stroke="#2f6bff"
            strokeWidth={2.5}
            fillOpacity={1}
            fill="url(#sgpaGradient)"
            activeDot={{ r: 5, fill: '#2f6bff', stroke: '#ffffff', strokeWidth: 2 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
export default SgpaTrend;
