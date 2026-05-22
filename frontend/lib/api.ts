/**
 * ErgoFlow AI — API Client
 * Fetch wrapper for the FastAPI backend at localhost:8000
 */

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
    apiFetch(`/api/telemetry/latest?user_id=${userId}`),
  getHistory: (userId: string, days = 7) =>
    apiFetch(`/api/telemetry/history?user_id=${userId}&days=${days}`),
};

// ── Feedback ──────────────────────────────────────────────────────────
export const feedbackApi = {
  submit: (data: { user_id: string; assessments: Record<string, number> }) =>
    apiFetch('/api/feedback/micro-prompt', {
      method: 'POST',
      body: JSON.stringify({ ...data, timestamp: new Date().toISOString() }),
    }),
  getHistory: (userId: string, limit = 20) =>
    apiFetch(`/api/feedback/history?user_id=${userId}&limit=${limit}`),
};

// ── Agent ─────────────────────────────────────────────────────────────
export const agentApi = {
  evaluate: (userId: string) =>
    apiFetch('/api/agent/evaluate', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    }),
  getActivity: (userId: string, limit = 30) =>
    apiFetch(`/api/agent/activity?user_id=${userId}&limit=${limit}`),
};

// ── Routines ──────────────────────────────────────────────────────────
export const routinesApi = {
  getNext: (userId: string) =>
    apiFetch(`/api/agent/routines/next?user_id=${userId}`),
  getHistory: (userId: string) =>
    apiFetch(`/api/agent/routines/history?user_id=${userId}`),
};

// ── Calendar ──────────────────────────────────────────────────────────
export const calendarApi = {
  getEvents: (userId: string) =>
    apiFetch(`/api/calendar/events?user_id=${userId}`),
};

// ── Simulator ─────────────────────────────────────────────────────────
export const simulatorApi = {
  generate: (data: { user_id?: string; scenario?: string; days?: number }) =>
    apiFetch('/api/simulator/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};
