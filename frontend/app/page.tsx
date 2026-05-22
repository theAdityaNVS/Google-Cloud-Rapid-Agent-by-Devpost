'use client';

import { useState, useEffect, useCallback } from 'react';

import Sidebar from '@/components/common/Sidebar';
import Header from '@/components/common/Header';
import FatigueScoreCard from '@/components/Dashboard/FatigueScoreCard';
import HealthTrendChart from '@/components/Dashboard/HealthTrendChart';
import CalendarSyncStatus from '@/components/Dashboard/CalendarSyncStatus';
import AgentActivityFeed from '@/components/Agent/AgentActivityFeed';
import MicroFeedbackModal from '@/components/Feedback/MicroFeedbackModal';
import RoutineCard from '@/components/Routine/RoutineCard';

import { 
  FeedbackAssessments, 
  BiometricTelemetry, 
  OrchestratedRoutine, 
  CalendarEvent, 
  AgentActivityEntry 
} from '@/lib/types';
import { 
  telemetryApi, 
  feedbackApi, 
  agentApi, 
  routinesApi, 
  calendarApi 
} from '@/lib/api';

export default function DashboardPage() {
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('dashboard');

  // Live Component States
  const [telemetryHistory, setTelemetryHistory] = useState<BiometricTelemetry[]>([]);
  const [nextRoutine, setNextRoutine] = useState<OrchestratedRoutine | null>(null);
  const [calendarEvents, setCalendarEvents] = useState<CalendarEvent[]>([]);
  const [activityFeed, setActivityFeed] = useState<AgentActivityEntry[]>([]);
  
  const [stats, setStats] = useState({
    currentSittingMins: 0,
    todaySteps: 0,
    todayStandHours: 0,
    hrv: 0,
    fatigueScore: 0.0,
  });

  // Fetch data function
  const refreshData = useCallback(async (triggerEval = false) => {
    try {
      if (triggerEval) {
        setEvaluating(true);
      }
      const userId = 'usr_dev_9981';

      let currentFatigue = stats.fatigueScore;
      if (triggerEval) {
        const evalResult = await agentApi.evaluate(userId) as any;
        if (evalResult && typeof evalResult.fatigue_score === 'number') {
          currentFatigue = evalResult.fatigue_score;
        }
      }

      // Fetch all dynamic data in parallel from the live Atlas backend
      const [latestTelemetry, history, routineData, events, feed] = await Promise.all([
        telemetryApi.getLatest(userId).catch(() => null) as Promise<BiometricTelemetry | null>,
        telemetryApi.getHistory(userId, 7).catch(() => []) as Promise<BiometricTelemetry[]>,
        routinesApi.getNext(userId).catch(() => null) as Promise<any>,
        calendarApi.getEvents(userId).catch(() => []) as Promise<CalendarEvent[]>,
        agentApi.getActivity(userId, 30).catch(() => []) as Promise<AgentActivityEntry[]>,
      ]);

      // If we didn't do a live evaluation, extract fatigue score from the latest decision activity log entry
      if (!triggerEval && feed.length > 0) {
        const decisionEntry = feed.find(
          (e) => e.entry_type === 'decision' && e.message.includes('Fatigue score computed')
        );
        if (decisionEntry) {
          const match = decisionEntry.message.match(/Fatigue score computed:\s*([0-9.]+)\/10/i);
          if (match && match[1]) {
            currentFatigue = parseFloat(match[1]);
          }
        }
      }

      setTelemetryHistory(history);
      
      // Parse routine status gracefully
      if (routineData && 'generated_protocol' in routineData) {
        setNextRoutine(routineData as OrchestratedRoutine);
      } else {
        setNextRoutine(null);
      }

      setCalendarEvents(events);
      
      // Reverse history so that timeline rolls chronologically (oldest at top -> latest at bottom)
      setActivityFeed([...feed].reverse());

      if (latestTelemetry) {
        setStats({
          currentSittingMins: latestTelemetry.context?.consecutive_sitting_mins ?? 0,
          todaySteps: latestTelemetry.metrics?.steps_count_today ?? 0,
          todayStandHours: latestTelemetry.metrics?.stand_hours_today ?? 0,
          hrv: latestTelemetry.metrics?.heart_rate_variability_hrv_ms ?? 0,
          fatigueScore: currentFatigue || 4.2,
        });
      } else {
        // Default base stats if telemetry is not loaded
        setStats((prev) => ({
          ...prev,
          fatigueScore: currentFatigue || 4.2,
        }));
      }
      setError(null);
    } catch (err: any) {
      console.error('Error fetching dashboard data:', err);
      setError('Unable to sync with ErgoFlow Agent backend. Reconnecting...');
    } finally {
      setLoading(false);
      setEvaluating(false);
    }
  }, [stats.fatigueScore]);

  // Initial load
  useEffect(() => {
    const init = async () => {
      // First load fast
      await refreshData(false);
      // Trigger live evaluation if no activity entries exist yet to kick off the agent!
      const userId = 'usr_dev_9981';
      const feed = await agentApi.getActivity(userId, 5).catch(() => []);
      if (feed.length === 0) {
        await refreshData(true);
      }
    };
    init();

    // Poll for updates every 10 seconds to keep the agent feed and metrics alive!
    const interval = setInterval(() => {
      refreshData(false);
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  // Handle post check-in submission
  const handleFeedbackSubmit = async (assessments: FeedbackAssessments) => {
    try {
      setEvaluating(true);
      const userId = 'usr_dev_9981';
      
      console.log('Submitting check-in assessments:', assessments);
      
      // 1. Send feedback to MongoDB Atlas
      await feedbackApi.submit({
        user_id: userId,
        assessments: assessments as unknown as Record<string, number>,
      });

      // 2. Immediately trigger ErgoFlow Agent evaluation
      // This will pull the fresh feedback, re-score fatigue, schedule routine & calendar event
      await refreshData(true);
      setFeedbackOpen(false);
    } catch (err) {
      console.error('Error submitting check-in feedback:', err);
      setError('Post-evaluation check-in failed. Try again.');
      setEvaluating(false);
    }
  };

  return (
    <div className="app-layout">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      <Header onOpenFeedback={() => setFeedbackOpen(true)} />

      <main className="main-content">
        {/* ── Status Header / Banner ────────────────────────────── */}
        {error && (
          <div className="glass-card error-banner animate-fade-in" style={{
            margin: '0 24px 20px',
            borderColor: '#ef4444',
            background: 'rgba(239, 68, 68, 0.05)',
            color: '#fca5a5',
            padding: '12px 16px',
            fontSize: '14px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span>⚠️ {error}</span>
            <button className="btn btn-secondary" onClick={() => refreshData(true)} style={{ padding: '4px 10px', fontSize: '12px' }}>
              Retry Connect
            </button>
          </div>
        )}

        {evaluating && (
          <div className="evaluating-overlay animate-fade-in" style={{
            margin: '0 24px 20px',
            background: 'linear-gradient(90deg, rgba(59, 130, 246, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%)',
            border: '1px solid rgba(255, 255, 255, 0.05)',
            borderRadius: '12px',
            padding: '12px 16px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            fontSize: '14px',
            color: '#f1f5f9'
          }}>
            <span className="spinner" style={{
              display: 'inline-block',
              width: '16px',
              height: '16px',
              border: '2px solid rgba(255,255,255,0.2)',
              borderTopColor: '#3b82f6',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }}></span>
            <span>🧠 ErgoFlow Agent is active: Re-scoring biometrics, planning interventions, and syncing calendar...</span>
            <style>{`
              @keyframes spin { to { transform: rotate(360deg); } }
            `}</style>
          </div>
        )}

        {activeTab === 'dashboard' && (
        <div className="page-content">
          {/* ── Stats Row ─────────────────────────────────────────── */}
          <div className="dashboard-grid animate-fade-in">
            <div className="glass-card stat-card">
              <div className="card-header">
                <span className="card-icon">🪑</span>
              </div>
              <div className={`stat-value ${stats.currentSittingMins >= 90 ? 'text-critical' : 'text-calm'}`}>
                {loading ? '...' : stats.currentSittingMins}
              </div>
              <div className="stat-label">Consecutive Sitting (min)</div>
              <div className={`stat-trend ${stats.currentSittingMins >= 90 ? 'up' : 'down'}`}>
                {stats.currentSittingMins >= 90 ? '↑ Above 90-min limit' : '↓ Safe sitting window'}
              </div>
            </div>

            <div className="glass-card stat-card">
              <div className="card-header">
                <span className="card-icon">👟</span>
              </div>
              <div className="stat-value text-warning">
                {loading ? '...' : stats.todaySteps.toLocaleString()}
              </div>
              <div className="stat-label">Steps Today</div>
              <div className="stat-trend down">
                {stats.todaySteps < 4000 ? '↓ 83% below target' : '↑ Making active progress'}
              </div>
            </div>

            <div className="glass-card stat-card">
              <div className="card-header">
                <span className="card-icon">🧍</span>
              </div>
              <div className="stat-value text-calm">
                {loading ? '...' : stats.todayStandHours}h
              </div>
              <div className="stat-label">Stand Hours Today</div>
              <div className="stat-trend neutral">Target: 4h</div>
            </div>

            <div className="glass-card stat-card">
              <div className="card-header">
                <span className="card-icon">💓</span>
              </div>
              <div className={`stat-value ${stats.hrv < 60 ? 'text-warning' : 'text-calm'}`}>
                {loading ? '...' : stats.hrv}
              </div>
              <div className="stat-label">HRV (ms)</div>
              <div className={`stat-trend ${stats.hrv < 60 ? 'up' : 'down'}`}>
                {stats.hrv < 60 ? '↓ Below baseline' : '↑ Normal autonomic state'}
              </div>
            </div>
          </div>

          {/* ── Main Row: Chart + Fatigue Score ────────────────────── */}
          <div className="dashboard-main-row animate-fade-in" style={{ animationDelay: '100ms' }}>
            <HealthTrendChart data={telemetryHistory} />
            <FatigueScoreCard score={stats.fatigueScore} />
          </div>

          {/* ── Bottom Row: Agent Feed + Routine/Calendar ──────────── */}
          <div className="dashboard-bottom-row animate-fade-in" style={{ animationDelay: '200ms' }}>
            <AgentActivityFeed entries={activityFeed} />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <RoutineCard routine={nextRoutine} />
              <CalendarSyncStatus events={calendarEvents} />
            </div>
          </div>
        </div>
        )}

        {activeTab === 'agent' && (
          <div className="page-content animate-fade-in">
             <h2 style={{ color: '#f8fafc', marginBottom: '24px' }}>Agent Reasoning Trace</h2>
             <AgentActivityFeed entries={activityFeed} />
          </div>
        )}

        {activeTab === 'routines' && (
          <div className="page-content animate-fade-in">
             <h2 style={{ color: '#f8fafc', marginBottom: '24px' }}>Scheduled Routines</h2>
             <div style={{ maxWidth: '400px' }}>
               <RoutineCard routine={nextRoutine} />
             </div>
          </div>
        )}

        {activeTab === 'calendar' && (
          <div className="page-content animate-fade-in">
             <h2 style={{ color: '#f8fafc', marginBottom: '24px' }}>Calendar Synchronization</h2>
             <div style={{ maxWidth: '600px' }}>
               <CalendarSyncStatus events={calendarEvents} />
             </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="page-content animate-fade-in">
             <h2 style={{ color: '#f8fafc', marginBottom: '24px' }}>Health Trends Analytics</h2>
             <HealthTrendChart data={telemetryHistory} />
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="page-content animate-fade-in">
             <h2 style={{ color: '#f8fafc', marginBottom: '24px' }}>User Settings</h2>
             <div className="glass-card" style={{ padding: '32px', textAlign: 'center', color: '#94a3b8' }}>
               <p>Settings panel coming soon! (Tier 3 feature)</p>
             </div>
          </div>
        )}
      </main>

      {/* ── Feedback Modal ─────────────────────────────────────────── */}
      <MicroFeedbackModal
        isOpen={feedbackOpen}
        onClose={() => setFeedbackOpen(false)}
        onSubmit={handleFeedbackSubmit}
      />
    </div>
  );
}
