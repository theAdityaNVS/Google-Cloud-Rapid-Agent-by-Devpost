'use client';

import { OrchestratedRoutine } from '@/lib/types';

interface RoutineCardProps {
  routine: OrchestratedRoutine;
}

const areaIcons: Record<string, string> = {
  lower_back: '🦴',
  shoulder: '💪',
  neck: '🦒',
  eyes: '👁️',
  general: '🏃',
  wrist: '🤚',
};

export default function RoutineCard({ routine }: { routine: OrchestratedRoutine | null }) {
  if (!routine) {
    return (
      <div className="glass-card routine-card">
        <div className="card-header">
          <div>
            <div className="card-title">Next Recovery Session</div>
            <div className="card-subtitle">Auto-scheduled by ErgoFlow Agent</div>
          </div>
          <span className="card-icon">🏋️</span>
        </div>
        <div className="all-clear-container" style={{
          padding: '24px 0',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          gap: '12px'
        }}>
          <div className="all-clear-check" style={{
            fontSize: '48px',
            color: '#10b981',
            background: 'rgba(16, 185, 129, 0.1)',
            width: '80px',
            height: '80px',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>✓</div>
          <div className="all-clear-title" style={{
            fontSize: '18px',
            fontWeight: 600,
            color: '#f8fafc'
          }}>All Clear & Dynamic</div>
          <p className="all-clear-desc" style={{
            fontSize: '14px',
            color: '#64748b',
            maxWidth: '300px',
            margin: 0
          }}>
            No intervention required. Biometric telemetry looks healthy and active. Keep moving!
          </p>
        </div>
      </div>
    );
  }

  const { generated_protocol: protocol } = routine;
  const scheduledTime = new Date(routine.scheduled_timestamp).toLocaleTimeString('en-US', {
    hour: '2-digit', minute: '2-digit',
  });

  return (
    <div className="glass-card routine-card">
      <div className="card-header">
        <div>
          <div className="card-title">Next Recovery Session</div>
          <div className="card-subtitle">Auto-scheduled by ErgoFlow Agent</div>
        </div>
        <span className="card-icon">🏋️</span>
      </div>

      <div className="routine-title">{protocol.title}</div>
      <div className="routine-meta">
        <span>⏱️ {protocol.duration_mins} min</span>
        <span>📅 {scheduledTime}</span>
        <span>🔄 {routine.status}</span>
      </div>

      <div className="exercise-list">
        {protocol.movements.map((move, i) => (
          <div key={i} className="exercise-item animate-slide-in" style={{ animationDelay: `${i * 80}ms` }}>
            <div className="exercise-number">{i + 1}</div>
            <div>
              <div className="exercise-name">
                {areaIcons[move.body_area] || '🏃'} {move.name}
              </div>
              <div className="exercise-desc">{move.description}</div>
              <div className="exercise-duration">⏱️ {move.duration_secs}s</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
