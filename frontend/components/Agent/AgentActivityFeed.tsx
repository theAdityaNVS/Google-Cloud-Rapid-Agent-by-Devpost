'use client';

import { AgentActivityEntry } from '@/lib/types';

interface AgentActivityFeedProps {
  entries: AgentActivityEntry[];
}

const typeIcons: Record<string, string> = {
  tool_call: '🔧',
  analysis: '📊',
  decision: '🧠',
  action: '⚡',
  result: '✅',
};

export default function AgentActivityFeed({ entries }: AgentActivityFeedProps) {
  return (
    <div className="glass-card">
      <div className="card-header">
        <div>
          <div className="card-title">Agent Activity</div>
          <div className="card-subtitle">Real-time reasoning trace</div>
        </div>
        <span className="card-icon">🤖</span>
      </div>

      <div className="activity-feed">
        {entries.map((entry, i) => {
          const time = new Date(entry.created_at).toLocaleTimeString('en-US', {
            hour: '2-digit', minute: '2-digit',
          });
          const isLatest = i === entries.length - 1;

          return (
            <div
              key={i}
              className={`activity-entry animate-slide-in ${isLatest ? 'latest' : ''}`}
              style={{ animationDelay: `${i * 50}ms` }}
            >
              <span className="activity-time">{time}</span>
              <span className="activity-icon">{typeIcons[entry.entry_type] || '📌'}</span>
              <span className="activity-message">{entry.message}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
