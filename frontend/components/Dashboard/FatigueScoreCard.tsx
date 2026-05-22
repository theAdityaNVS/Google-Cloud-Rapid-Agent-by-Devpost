'use client';

import { useMemo } from 'react';

interface FatigueScoreCardProps {
  score: number;  // 0-10
}

export default function FatigueScoreCard({ score }: FatigueScoreCardProps) {
  const { color, level, levelClass } = useMemo(() => {
    if (score >= 7) return { color: '#ef4444', level: 'High Risk', levelClass: 'high' };
    if (score >= 4) return { color: '#f59e0b', level: 'Moderate', levelClass: 'moderate' };
    return { color: '#10b981', level: 'Low', levelClass: 'low' };
  }, [score]);

  const radius = 65;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / 10) * circumference;
  const dashOffset = circumference - progress;

  return (
    <div className="glass-card stat-card">
      <div className="card-header">
        <div>
          <div className="card-title">Fatigue Score</div>
          <div className="card-subtitle">Real-time assessment</div>
        </div>
        <span className="card-icon">🧠</span>
      </div>

      <div className="fatigue-ring-container">
        <div className="fatigue-ring">
          <svg viewBox="0 0 160 160">
            <circle className="fatigue-ring-bg" cx="80" cy="80" r={radius} />
            <circle
              className="fatigue-ring-progress"
              cx="80" cy="80" r={radius}
              stroke={color}
              strokeDasharray={circumference}
              strokeDashoffset={dashOffset}
              style={{ filter: `drop-shadow(0 0 6px ${color}40)` }}
            />
          </svg>
          <div className="fatigue-ring-center">
            <div className="fatigue-score-value" style={{ color }}>{score.toFixed(1)}</div>
            <div className="fatigue-score-label">/ 10</div>
          </div>
        </div>
        <div className={`fatigue-level ${levelClass}`}>{level}</div>
      </div>
    </div>
  );
}
