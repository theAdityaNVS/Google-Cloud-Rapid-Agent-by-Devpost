'use client';

import { useState, useEffect } from 'react';

export default function Header({ onOpenFeedback }: { onOpenFeedback: () => void }) {
  const [time, setTime] = useState('');

  useEffect(() => {
    const update = () => {
      setTime(new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    };
    update();
    const id = setInterval(update, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <header className="header">
      <h1 className="header-title">Health Dashboard</h1>

      <div className="header-right">
        <span className="header-time">{time}</span>

        <div className="status-badge active">
          <span className="status-dot"></span>
          Agent Active
        </div>

        <button className="btn btn-primary" onClick={onOpenFeedback}>
          🩺 Quick Check-In
        </button>
      </div>
    </header>
  );
}
