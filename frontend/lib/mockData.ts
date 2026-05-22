import { BiometricTelemetry, SubjectiveFeedback, AgentActivityEntry, OrchestratedRoutine, CalendarEvent } from './types';

/* ═══════════════════════════════════════════════════════════════════════
   ErgoFlow AI — Mock Data for Development & Demo
   Realistic data that makes the dashboard look alive
   ═══════════════════════════════════════════════════════════════════════ */

const now = new Date();
const hours = (h: number, m = 0) => {
  const d = new Date(now);
  d.setHours(h, m, 0, 0);
  return d.toISOString();
};
const daysAgo = (days: number, h = 14, m = 0) => {
  const d = new Date(now);
  d.setDate(d.getDate() - days);
  d.setHours(h, m, 0, 0);
  return d.toISOString();
};

// ── Telemetry History (7 days) ────────────────────────────────────────
export const mockTelemetryHistory: BiometricTelemetry[] = [
  { user_id: 'usr_dev_9981', timestamp: daysAgo(6, 14), metrics: { stand_hours_today: 3.5, active_calories_burned: 220, steps_count_today: 4200, heart_rate_variability_hrv_ms: 58 }, context: { current_calendar_state: 'free', consecutive_sitting_mins: 35 } },
  { user_id: 'usr_dev_9981', timestamp: daysAgo(5, 15), metrics: { stand_hours_today: 2.0, active_calories_burned: 150, steps_count_today: 2100, heart_rate_variability_hrv_ms: 45 }, context: { current_calendar_state: 'in_deep_focus_block', consecutive_sitting_mins: 95 } },
  { user_id: 'usr_dev_9981', timestamp: daysAgo(4, 16), metrics: { stand_hours_today: 1.5, active_calories_burned: 110, steps_count_today: 1200, heart_rate_variability_hrv_ms: 38 }, context: { current_calendar_state: 'in_deep_focus_block', consecutive_sitting_mins: 130 } },
  { user_id: 'usr_dev_9981', timestamp: daysAgo(3, 14), metrics: { stand_hours_today: 4.0, active_calories_burned: 280, steps_count_today: 5800, heart_rate_variability_hrv_ms: 62 }, context: { current_calendar_state: 'free', consecutive_sitting_mins: 20 } },
  { user_id: 'usr_dev_9981', timestamp: daysAgo(2, 17), metrics: { stand_hours_today: 1.0, active_calories_burned: 90, steps_count_today: 800, heart_rate_variability_hrv_ms: 32 }, context: { current_calendar_state: 'in_deep_focus_block', consecutive_sitting_mins: 145 } },
  { user_id: 'usr_dev_9981', timestamp: daysAgo(1, 15), metrics: { stand_hours_today: 2.5, active_calories_burned: 180, steps_count_today: 3100, heart_rate_variability_hrv_ms: 48 }, context: { current_calendar_state: 'in_meeting', consecutive_sitting_mins: 75 } },
  { user_id: 'usr_dev_9981', timestamp: hours(14, 30), metrics: { stand_hours_today: 1.0, active_calories_burned: 95, steps_count_today: 840, heart_rate_variability_hrv_ms: 35 }, context: { current_calendar_state: 'in_deep_focus_block', consecutive_sitting_mins: 120 } },
];

// ── Feedback History ──────────────────────────────────────────────────
export const mockFeedbackHistory: SubjectiveFeedback[] = [
  { user_id: 'usr_dev_9981', timestamp: daysAgo(2, 11), assessments: { lower_back_stiffness: 2, shoulder_tension: 2, neck_pain: 1, eye_strain: 2, mental_fatigue: 1 } },
  { user_id: 'usr_dev_9981', timestamp: daysAgo(1, 14), assessments: { lower_back_stiffness: 3, shoulder_tension: 3, neck_pain: 2, eye_strain: 3, mental_fatigue: 2 } },
  { user_id: 'usr_dev_9981', timestamp: hours(14, 32), assessments: { lower_back_stiffness: 4, shoulder_tension: 4, neck_pain: 3, eye_strain: 3, mental_fatigue: 3 } },
];

// ── Agent Activity Feed ───────────────────────────────────────────────
export const mockActivityFeed: AgentActivityEntry[] = [
  { user_id: 'usr_dev_9981', created_at: hours(14, 33, ), entry_type: 'tool_call', message: '📡 Querying MongoDB MCP → biometric_telemetry collection', metadata: { tool: 'mongodb_mcp' } },
  { user_id: 'usr_dev_9981', created_at: hours(14, 33), entry_type: 'tool_call', message: '📡 Querying MongoDB MCP → subjective_feedback collection', metadata: { tool: 'mongodb_mcp' } },
  { user_id: 'usr_dev_9981', created_at: hours(14, 34), entry_type: 'analysis', message: '📊 Biometric data received — Sitting: 120 mins, Steps: 840', metadata: { sitting_mins: 120, steps: 840 } },
  { user_id: 'usr_dev_9981', created_at: hours(14, 34), entry_type: 'analysis', message: '📋 Feedback data — Back: 4/5, Shoulder: 4/5, Neck: 3/5, Eyes: 3/5' },
  { user_id: 'usr_dev_9981', created_at: hours(14, 35), entry_type: 'decision', message: '🧠 Fatigue score computed: 8.2/10 — HIGH — intervention needed', metadata: { fatigue_score: 8.2 } },
  { user_id: 'usr_dev_9981', created_at: hours(14, 35), entry_type: 'decision', message: '🚨 Threshold exceeded — initiating autonomous intervention' },
  { user_id: 'usr_dev_9981', created_at: hours(14, 35), entry_type: 'tool_call', message: '📅 Checking Google Calendar for available slots', metadata: { tool: 'google_calendar' } },
  { user_id: 'usr_dev_9981', created_at: hours(14, 36), entry_type: 'analysis', message: '✅ Available slot found: 15:00 – 15:10 UTC' },
  { user_id: 'usr_dev_9981', created_at: hours(14, 36), entry_type: 'action', message: '📝 Generated routine: "Developer Lumbar & Shoulder Recovery Protocol" — 4 exercises, 8 min' },
  { user_id: 'usr_dev_9981', created_at: hours(14, 36), entry_type: 'action', message: '💾 Routine saved to MongoDB → orchestrated_routines collection' },
  { user_id: 'usr_dev_9981', created_at: hours(14, 37), entry_type: 'action', message: '📅 Calendar event created: "ErgoFlow: Developer Lumbar & Shoulder Recovery Protocol"' },
  { user_id: 'usr_dev_9981', created_at: hours(14, 37), entry_type: 'result', message: '✅ Intervention complete — Recovery protocol scheduled at 15:00 UTC', metadata: { fatigue_score: 8.2 } },
];

// ── Current Routine ───────────────────────────────────────────────────
export const mockCurrentRoutine: OrchestratedRoutine = {
  user_id: 'usr_dev_9981',
  scheduled_timestamp: hours(15, 0),
  associated_calendar_event_id: 'cal_evt_382917',
  status: 'scheduled',
  generated_protocol: {
    title: 'Developer Lumbar & Shoulder Recovery Protocol',
    duration_mins: 8,
    movements: [
      { name: 'Seated Cat-Cow Stretch', duration_secs: 120, description: 'Alternate between arching and rounding your spine while seated. Mobilizes thoracic and lumbar vertebrae.', body_area: 'lower_back' },
      { name: 'Doorway Pec Stretch', duration_secs: 120, description: 'Place forearm on a door frame at 90°. Step through to stretch the pectoral and anterior deltoid.', body_area: 'shoulder' },
      { name: 'Chin Tucks', duration_secs: 60, description: 'Retract chin straight back, creating a double chin. Hold 5 seconds, repeat 10 times.', body_area: 'neck' },
      { name: '20-20-20 Eye Rest Protocol', duration_secs: 60, description: 'Look at an object 20 feet away for 20 seconds to reset ciliary muscles.', body_area: 'eyes' },
    ],
  },
};

// ── Calendar Events ───────────────────────────────────────────────────
export const mockCalendarEvents: CalendarEvent[] = [
  { user_id: 'usr_dev_9981', event_id: 'cal_evt_382917', title: 'ErgoFlow: Lumbar & Shoulder Recovery', start_time: hours(15, 0), end_time: hours(15, 10), description: 'Auto-scheduled recovery. Fatigue: 8.2/10', status: 'confirmed' },
  { user_id: 'usr_dev_9981', event_id: 'cal_evt_291043', title: 'ErgoFlow: Eye Strain Reset', start_time: daysAgo(1, 16), end_time: daysAgo(1, 16), description: 'Auto-scheduled. Fatigue: 6.5/10', status: 'confirmed' },
];

// ── Summary Stats ─────────────────────────────────────────────────────
export const mockStats = {
  currentSittingMins: 120,
  todaySteps: 840,
  todayStandHours: 1.0,
  hrv: 35,
  fatigueScore: 8.2,
  routinesThisWeek: 4,
  avgFatigueScore: 5.8,
};
