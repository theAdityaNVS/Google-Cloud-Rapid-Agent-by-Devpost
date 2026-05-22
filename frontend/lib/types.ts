/* TypeScript types matching backend Pydantic models */

export interface TelemetryMetrics {
  stand_hours_today: number;
  active_calories_burned: number;
  steps_count_today: number;
  heart_rate_variability_hrv_ms: number;
}

export interface TelemetryContext {
  current_calendar_state: 'in_deep_focus_block' | 'in_meeting' | 'free';
  consecutive_sitting_mins: number;
}

export interface BiometricTelemetry {
  user_id: string;
  timestamp: string;
  metrics: TelemetryMetrics;
  context: TelemetryContext;
}

export interface FeedbackAssessments {
  lower_back_stiffness: number;
  shoulder_tension: number;
  neck_pain: number;
  eye_strain: number;
  mental_fatigue: number;
}

export interface SubjectiveFeedback {
  user_id: string;
  timestamp: string;
  assessments: FeedbackAssessments;
}

export interface Movement {
  name: string;
  duration_secs: number;
  description: string;
  body_area: string;
}

export interface GeneratedProtocol {
  title: string;
  duration_mins: number;
  movements: Movement[];
}

export interface OrchestratedRoutine {
  user_id: string;
  scheduled_timestamp: string;
  associated_calendar_event_id: string | null;
  status: 'scheduled' | 'in_progress' | 'completed' | 'dismissed';
  generated_protocol: GeneratedProtocol;
}

export interface AgentActivityEntry {
  user_id: string;
  created_at: string;
  entry_type: 'analysis' | 'decision' | 'action' | 'tool_call' | 'result';
  message: string;
  metadata?: Record<string, unknown>;
}

export interface CalendarEvent {
  user_id: string;
  event_id: string;
  title: string;
  start_time: string;
  end_time: string;
  description: string;
  status: 'confirmed' | 'cancelled';
}

export interface AgentEvaluationResult {
  fatigue_score: number;
  reasoning: string[];
  action_taken: 'intervention_scheduled' | 'no_action_needed';
  routine: OrchestratedRoutine | null;
  calendar_event: CalendarEvent | null;
}
