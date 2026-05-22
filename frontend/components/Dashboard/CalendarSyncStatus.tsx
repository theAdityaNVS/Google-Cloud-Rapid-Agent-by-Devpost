'use client';

import { CalendarEvent } from '@/lib/types';

interface CalendarSyncStatusProps {
  events: CalendarEvent[];
}

export default function CalendarSyncStatus({ events }: CalendarSyncStatusProps) {
  return (
    <div className="glass-card">
      <div className="card-header">
        <div>
          <div className="card-title">Calendar Sync</div>
          <div className="card-subtitle">Agent-scheduled events</div>
        </div>
        <span className="card-icon">📅</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {events.map((event, i) => {
          const start = new Date(event.start_time).toLocaleTimeString('en-US', {
            hour: '2-digit', minute: '2-digit',
          });
          return (
            <div key={i} className="calendar-event animate-slide-in" style={{ animationDelay: `${i * 100}ms` }}>
              <span className="calendar-event-time">{start}</span>
              <div>
                <div className="calendar-event-title">{event.title}</div>
                <div className="calendar-event-desc">{event.description}</div>
              </div>
              <span className={`calendar-event-status ${event.status}`}>{event.status}</span>
            </div>
          );
        })}

        {events.length === 0 && (
          <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-muted)', fontSize: '13px' }}>
            No upcoming events
          </div>
        )}
      </div>
    </div>
  );
}
