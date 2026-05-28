import { 
  BiometricTelemetry, 
  OrchestratedRoutine, 
  CalendarEvent, 
  AgentActivityEntry,
  AgentEvaluationResult
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// ── Telemetry ─────────────────────────────────────────────────────────
export const telemetryApi = {
  getLatest: (userId: string) =>
    apiFetch<BiometricTelemetry | null>(`/api/telemetry/latest?user_id=${userId}`),
  getHistory: (userId: string, days = 7) =>
    apiFetch<BiometricTelemetry[]>(`/api/telemetry/history?user_id=${userId}&days=${days}`),
};

// ── Feedback ──────────────────────────────────────────────────────────
export const feedbackApi = {
  submit: (data: { user_id: string; assessments: Record<string, number> }) =>
    apiFetch<any>('/api/feedback/micro-prompt', {
      method: 'POST',
      body: JSON.stringify({ ...data, timestamp: new Date().toISOString() }),
    }),
  getHistory: (userId: string, limit = 20) =>
    apiFetch<any[]>(`/api/feedback/history?user_id=${userId}&limit=${limit}`),
};

// ── Agent ─────────────────────────────────────────────────────────────
export const agentApi = {
  evaluate: (userId: string) =>
    apiFetch<AgentEvaluationResult>('/api/agent/evaluate', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    }),
  getActivity: (userId: string, limit = 30) =>
    apiFetch<AgentActivityEntry[]>(`/api/agent/activity?user_id=${userId}&limit=${limit}`),
};

// ── Routines ──────────────────────────────────────────────────────────
export const routinesApi = {
  getNext: (userId: string) =>
    apiFetch<OrchestratedRoutine | null>(`/api/agent/routines/next?user_id=${userId}`),
  getHistory: (userId: string) =>
    apiFetch<OrchestratedRoutine[]>(`/api/agent/routines/history?user_id=${userId}`),
};

// ── Calendar ──────────────────────────────────────────────────────────
export const calendarApi = {
  getEvents: (userId: string) =>
    apiFetch<CalendarEvent[]>(`/api/calendar/events?user_id=${userId}`),
};

// ── Simulator ─────────────────────────────────────────────────────────
export const simulatorApi = {
  generate: (data: { user_id?: string; scenario?: string; days?: number }) =>
    apiFetch<any>('/api/simulator/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};
