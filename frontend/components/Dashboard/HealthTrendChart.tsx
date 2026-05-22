'use client';

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { BiometricTelemetry } from '@/lib/types';

interface HealthTrendChartProps {
  data: BiometricTelemetry[];
}

export default function HealthTrendChart({ data }: HealthTrendChartProps) {
  const chartData = data.map((d) => {
    const date = new Date(d.timestamp);
    return {
      day: date.toLocaleDateString('en-US', { weekday: 'short' }),
      sittingMins: d.context.consecutive_sitting_mins,
      steps: Math.round(d.metrics.steps_count_today / 100),  // Scale for chart
      hrv: d.metrics.heart_rate_variability_hrv_ms,
      standHours: d.metrics.stand_hours_today,
    };
  });

  return (
    <div className="glass-card">
      <div className="card-header">
        <div>
          <div className="card-title">Health Trends — 7 Days</div>
          <div className="card-subtitle">Sitting time vs. activity levels</div>
        </div>
        <span className="card-icon">📈</span>
      </div>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={0}>
          <AreaChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="gradientSitting" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#ef4444" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#ef4444" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gradientSteps" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#10b981" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gradientHRV" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis dataKey="day" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip
              contentStyle={{
                background: '#111827',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '12px',
                color: '#f1f5f9',
                fontSize: '12px',
              }}
            />
            <Legend wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />
            <Area type="monotone" dataKey="sittingMins" name="Sitting (mins)" stroke="#ef4444" fill="url(#gradientSitting)" strokeWidth={2} />
            <Area type="monotone" dataKey="steps" name="Steps (×100)" stroke="#10b981" fill="url(#gradientSteps)" strokeWidth={2} />
            <Area type="monotone" dataKey="hrv" name="HRV (ms)" stroke="#3b82f6" fill="url(#gradientHRV)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
