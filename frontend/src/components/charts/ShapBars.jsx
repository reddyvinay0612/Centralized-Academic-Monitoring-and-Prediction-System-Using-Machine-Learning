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

export function ShapBars({ explanations = [], studentName = 'Student' }) {
  if (!explanations || explanations.length === 0) {
    return (
      <div className="flex h-48 items-center justify-center rounded-input border border-dashed border-line p-4 text-center text-caption text-muted">
        No SHAP attribution vectors available for this prediction instance.
      </div>
    );
  }

  // Format data for diverging bar chart
  const data = explanations.map((item) => {
    const val = Number(item.shap !== undefined ? item.shap : (item.shap_value || 0));
    return {
      feature: item.feature || item.feature_name || 'Feature',
      displayValue: item.displayValue || item.feature_value || '',
      shap: val,
      // Color: positive SHAP pushes towards high risk (red), negative pushes towards safe (green)
      color: val > 0 ? '#d9445a' : '#0f9d8a',
    };
  });

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload;
      const isRiskDriver = d.shap > 0;
      return (
        <div className="rounded-input border border-line bg-surface p-2.5 shadow-card dark:border-dark-line dark:bg-dark-surface">
          <p className="font-heading text-caption font-semibold text-ink dark:text-dark-text">{d.feature}</p>
          <p className="text-caption text-muted">Observed Value: <span className="font-medium text-ink dark:text-dark-text">{d.displayValue}</span></p>
          <p className="mt-1 text-caption font-semibold" style={{ color: d.color }}>
            {isRiskDriver ? 'Increases Risk' : 'Protective Factor'}: {d.shap > 0 ? `+${d.shap.toFixed(2)}` : d.shap.toFixed(2)} SHAP
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full">
      {/* Diverging Bar Chart */}
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 10, right: 30, left: 30, bottom: 10 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#d9e1ea" horizontal={false} opacity={0.6} />
            <XAxis
              type="number"
              domain={[-0.6, 0.6]}
              stroke="#5b6b82"
              fontSize={11}
              tickFormatter={(v) => (v > 0 ? `+${v}` : `${v}`)}
            />
            <YAxis
              type="category"
              dataKey="feature"
              stroke="#5b6b82"
              fontSize={12}
              width={160}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine x={0} stroke="#14213d" strokeWidth={1.5} />
            <Bar dataKey="shap" radius={[4, 4, 4, 4]} barSize={16}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Axis Guide */}
      <div className="mt-1 flex items-center justify-between px-6 text-[11px] font-medium">
        <span className="text-risk-low">&larr; Lowers Academic Risk (Protective)</span>
        <span className="text-muted dark:text-dark-muted">TreeSHAP Base Value = 0.0</span>
        <span className="text-risk-high">Increases Risk Driver &rarr;</span>
      </div>

      {/* Plain Language Synthesis */}
      <div className="mt-4 rounded-input border border-line bg-page/50 p-3 text-caption text-ink dark:border-dark-line dark:bg-dark-surface/50 dark:text-dark-text">
        <span className="font-semibold text-accent">XAI Interpretation: </span>
        {data.some((d) => d.shap > 0) ? (
          <span>
            Primary risk drivers for <b>{studentName}</b> are{' '}
            <b>{data.filter((d) => d.shap > 0).map((d) => d.feature).join(', ')}</b>. 
            Addressing these specific bottlenecks through targeted remedial mentoring will have the greatest impact on improving their academic trajectory.
          </span>
        ) : (
          <span>
            <b>{studentName}</b> exhibits strong protective attributes across attendance and CIE consistency, keeping predicted risk within the safe threshold.
          </span>
        )}
      </div>
    </div>
  );
}
export default ShapBars;
