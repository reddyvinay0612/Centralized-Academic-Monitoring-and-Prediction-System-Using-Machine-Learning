import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

export function DeptComparisonChart({ departments = [], height = 300 }) {
  if (!departments || departments.length === 0) {
    return (
      <div className="flex h-56 items-center justify-center text-caption text-muted">
        No departmental metrics available for comparative visualization.
      </div>
    );
  }

  const chartData = departments.map((d) => ({
    name: d.dept_code || d.name,
    fullName: d.name,
    attendance: Number(d.performance?.avg_attendance || 0),
    cgpa: Number(d.performance?.avg_cgpa || 0),
    students: Number(d.headcount?.students || 0),
    highRisk: Number(d.performance?.risk_breakdown?.high || 0)
  }));

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="rounded-lg border border-line bg-surface p-3 shadow-lg dark:border-dark-line dark:bg-dark-surface text-caption">
          <p className="font-heading font-bold text-ink dark:text-dark-text mb-1">
            {data.fullName} ({data.name})
          </p>
          <div className="space-y-1">
            <p className="text-accent font-semibold flex items-center justify-between gap-4">
              <span>Avg Attendance:</span>
              <span>{data.attendance}%</span>
            </p>
            <p className="text-emerald-600 dark:text-emerald-400 font-semibold flex items-center justify-between gap-4">
              <span>Cumulative CGPA:</span>
              <span>{data.cgpa} / 10.0</span>
            </p>
            <p className="text-muted flex items-center justify-between gap-4 border-t border-line/50 pt-1 dark:border-dark-line/50">
              <span>Enrolled Students:</span>
              <span className="font-bold text-ink dark:text-dark-text">{data.students}</span>
            </p>
            <p className="text-risk-high flex items-center justify-between gap-4">
              <span>High Risk Cohort:</span>
              <span className="font-bold">{data.highRisk}</span>
            </p>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 10, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#d9e1ea" vertical={false} opacity={0.6} />
          <XAxis
            dataKey="name"
            stroke="#5b6b82"
            fontSize={12}
            tickLine={false}
            axisLine={{ stroke: '#d9e1ea' }}
          />
          {/* Left Y-Axis: Attendance Percentage (0-100) */}
          <YAxis
            yAxisId="left"
            orientation="left"
            domain={[0, 100]}
            stroke="#2f6bff"
            fontSize={11}
            tickLine={false}
            unit="%"
          />
          {/* Right Y-Axis: Cumulative CGPA (0-10.0) */}
          <YAxis
            yAxisId="right"
            orientation="right"
            domain={[0, 10]}
            stroke="#0f9d8a"
            fontSize={11}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="top"
            height={36}
            formatter={(value) => (
              <span className="text-caption font-semibold text-ink dark:text-dark-text">{value}</span>
            )}
          />
          <Bar
            yAxisId="left"
            dataKey="attendance"
            name="Department Avg Attendance (%)"
            fill="#2f6bff"
            radius={[4, 4, 0, 0]}
            maxBarSize={38}
          />
          <Bar
            yAxisId="right"
            dataKey="cgpa"
            name="Cumulative CGPA (10.0 Scale)"
            fill="#0f9d8a"
            radius={[4, 4, 0, 0]}
            maxBarSize={38}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default DeptComparisonChart;
