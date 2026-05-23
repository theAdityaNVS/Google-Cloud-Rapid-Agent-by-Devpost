"""
ErgoFlow AI — Simulated Agent Service
Implements the fatigue-scoring and routine-generation logic that will
eventually be replaced by real Google Cloud Agent Builder + Gemini 3 calls.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models import (
    AgentActivityEntry, OrchestratedRoutine, GeneratedProtocol, Movement,
)
from app.services import mongodb_service as db_svc


# ── Exercise Library ──────────────────────────────────────────────────────
EXERCISE_LIBRARY = {
    "lower_back": [
        Movement(name="Seated Cat-Cow Stretch", duration_secs=120,
                 description="Alternate between arching and rounding your spine while seated. Mobilizes thoracic and lumbar vertebrae.",
                 body_area="lower_back"),
        Movement(name="Standing Lumbar Extension", duration_secs=90,
                 description="Stand and place hands on lower back. Gently lean backward, hold 5 seconds, repeat.",
                 body_area="lower_back"),
        Movement(name="Piriformis Stretch", duration_secs=120,
                 description="Cross ankle over opposite knee while seated. Lean forward gently to stretch the deep glute.",
                 body_area="lower_back"),
    ],
    "shoulder": [
        Movement(name="Doorway Pec Stretch", duration_secs=120,
                 description="Place forearm on a door frame at 90°. Step through to stretch the pectoral and anterior deltoid.",
                 body_area="shoulder"),
        Movement(name="Shoulder Rolls", duration_secs=60,
                 description="Roll shoulders forward 10 times, then backward 10 times. Releases trapezius tension.",
                 body_area="shoulder"),
        Movement(name="Cross-Body Shoulder Stretch", duration_secs=90,
                 description="Pull one arm across your chest with the opposite hand. Hold 15 seconds each side.",
                 body_area="shoulder"),
    ],
    "neck": [
        Movement(name="Chin Tucks", duration_secs=60,
                 description="Retract chin straight back, creating a double chin. Hold 5 seconds, repeat 10 times.",
                 body_area="neck"),
        Movement(name="Lateral Neck Stretch", duration_secs=90,
                 description="Tilt ear toward shoulder, gently assist with hand. Hold 15 seconds each side.",
                 body_area="neck"),
    ],
    "eyes": [
        Movement(name="20-20-20 Eye Rest Protocol", duration_secs=60,
                 description="Look at an object 20 feet away for 20 seconds to reset ciliary muscles.",
                 body_area="eyes"),
        Movement(name="Eye Circles", duration_secs=45,
                 description="Slowly roll eyes clockwise 5 times, then counter-clockwise 5 times.",
                 body_area="eyes"),
    ],
    "general": [
        Movement(name="Standing Desk Break", duration_secs=120,
                 description="Stand up, walk 50 steps, do 10 calf raises. Reactivates lower-body circulation.",
                 body_area="general"),
        Movement(name="Wrist Circles & Flexor Stretch", duration_secs=60,
                 description="Circle wrists 10x each direction, then extend arm and pull fingers back for 15s each hand.",
                 body_area="wrist"),
    ],
}


def _compute_fatigue_score(
    telemetry: Optional[Dict], feedback: Optional[Dict]
) -> float:
    """
    Compute a composite fatigue score (0-10) from the latest data.
    Weights: sitting=0.3, pain=0.3, inactivity=0.2, mental=0.2
    """
    sitting_score = 0.0
    pain_score = 0.0
    inactivity_score = 0.0
    mental_score = 0.0

    if telemetry:
        ctx = telemetry.get("context", {})
        metrics = telemetry.get("metrics", {})
        sitting_mins = ctx.get("consecutive_sitting_mins", 0)
        sitting_score = min(sitting_mins / 120.0, 1.0) * 10

        steps = metrics.get("steps_count_today", 5000)
        inactivity_score = max(1 - steps / 5000.0, 0) * 10

    if feedback:
        assess = feedback.get("assessments", {})
        back = assess.get("lower_back_stiffness", 1)
        shoulder = assess.get("shoulder_tension", 1)
        neck = assess.get("neck_pain", 1)
        pain_score = ((back + shoulder + neck) / 3.0) / 5.0 * 10

        mental = assess.get("mental_fatigue", 1)
        eyes = assess.get("eye_strain", 1)
        mental_score = ((mental + eyes) / 2.0) / 5.0 * 10

    final = (sitting_score * 0.3 + pain_score * 0.3
             + inactivity_score * 0.2 + mental_score * 0.2)
    return round(final, 1)


def _pick_exercises(feedback: Optional[Dict], count: int = 4) -> List[Movement]:
    """Select targeted exercises based on the highest pain areas."""
    priority_areas: List[str] = []
    if feedback:
        assess = feedback.get("assessments", {})
        scored = [
            ("lower_back", assess.get("lower_back_stiffness", 1)),
            ("shoulder", assess.get("shoulder_tension", 1)),
            ("neck", assess.get("neck_pain", 1)),
            ("eyes", assess.get("eye_strain", 1)),
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        priority_areas = [area for area, _ in scored if _ >= 2]

    if not priority_areas:
        priority_areas = ["general", "shoulder", "lower_back"]

    exercises: List[Movement] = []
    for area in priority_areas:
        pool = EXERCISE_LIBRARY.get(area, EXERCISE_LIBRARY["general"])
        exercises.append(random.choice(pool))
        if len(exercises) >= count:
            break

    # Fill remaining slots with general exercises
    while len(exercises) < count:
        exercises.append(random.choice(EXERCISE_LIBRARY["general"]))

    return exercises[:count]


def _pick_exercises_by_areas(targeted_areas: List[str], feedback: Optional[Dict], count: int = 4) -> List[Movement]:
    """Select exercises using Gemini-identified priority areas. Falls back to feedback-based selection."""
    if not targeted_areas:
        return _pick_exercises(feedback, count)

    exercises: List[Movement] = []
    for area in targeted_areas:
        pool = EXERCISE_LIBRARY.get(area, EXERCISE_LIBRARY["general"])
        exercises.append(random.choice(pool))
        if len(exercises) >= count:
            break

    while len(exercises) < count:
        exercises.append(random.choice(EXERCISE_LIBRARY["general"]))

    return exercises[:count]


def _generate_routine_title(fatigue_score: float, feedback: Optional[Dict]) -> str:
    """Generate a descriptive routine title based on primary issues."""
    if feedback:
        assess = feedback.get("assessments", {})
        issues = []
        if assess.get("lower_back_stiffness", 0) >= 3:
            issues.append("Lumbar")
        if assess.get("shoulder_tension", 0) >= 3:
            issues.append("Shoulder")
        if assess.get("neck_pain", 0) >= 3:
            issues.append("Neck")
        if assess.get("eye_strain", 0) >= 3:
            issues.append("Eye")
        if issues:
            return f"Developer {' & '.join(issues)} Recovery Protocol"
    if fatigue_score >= 8:
        return "Urgent Full-Body Recovery Protocol"
    if fatigue_score >= 6:
        return "Moderate Recovery & Mobility Session"
    return "Preventive Micro-Recovery Break"


async def evaluate_user(db: AsyncIOMotorDatabase, user_id: str) -> Dict[str, Any]:
    """
    Run the agent evaluation loop.
    Tries Gemini agent first; falls back to local simulation if key not configured.
    """
    activity_entries: List[AgentActivityEntry] = []
    now = datetime.now(timezone.utc)

    def _log(entry_type: str, message: str, metadata: Optional[Dict] = None):
        activity_entries.append(AgentActivityEntry(
            user_id=user_id,
            created_at=now + timedelta(seconds=len(activity_entries)),
            entry_type=entry_type,
            message=message,
            metadata=metadata,
        ))

    # Try real Gemini agent first
    from app.services.gemini_agent import run_agent
    from app.config import settings

    gemini_decision: Optional[Dict] = None
    if settings.gemini_api_key:
        try:
            _log("tool_call", "🤖 Invoking Gemini agent with MongoDB MCP tools",
                 {"model": settings.gemini_model, "mcp_server": settings.mcp_server_url})
            gemini_decision = await run_agent(user_id)
            _log("analysis", "✅ Gemini agent returned decision",
                 {"fatigue_score": gemini_decision.get("fatigue_score")})
            for step in gemini_decision.get("reasoning", []):
                _log("analysis", f"🧠 {step}")
        except Exception as exc:
            _log("analysis", f"⚠️ Gemini agent failed ({exc}), falling back to simulation")
            gemini_decision = None

    # Fallback: use local simulation
    if gemini_decision is None:
        _log("tool_call", "📡 Querying MongoDB MCP → biometric_telemetry (simulated)",
             {"tool": "mongodb_mcp", "collection": "biometric_telemetry"})
        telemetry = await db_svc.get_latest_telemetry(db, user_id)
        _log("tool_call", "📡 Querying MongoDB MCP → subjective_feedback (simulated)",
             {"tool": "mongodb_mcp", "collection": "subjective_feedback"})
        feedback = await db_svc.get_latest_feedback(db, user_id)
        fatigue_score = _compute_fatigue_score(telemetry, feedback)
        _log("decision",
             f"🧠 Fatigue score computed: {fatigue_score}/10 "
             f"({'HIGH — intervention needed' if fatigue_score >= 6 else 'Acceptable'})",
             {"fatigue_score": fatigue_score})
        gemini_decision = {
            "fatigue_score": fatigue_score,
            "reasoning": [e.message for e in activity_entries],
            "action": "intervention_scheduled" if fatigue_score >= 6 else "no_action_needed",
            "targeted_areas": [],
        }
        if fatigue_score >= 6:
            fb_data = await db_svc.get_latest_feedback(db, user_id)
            gemini_decision["routine_title"] = _generate_routine_title(fatigue_score, fb_data)

    fatigue_score = gemini_decision["fatigue_score"]
    action = gemini_decision.get("action", "no_action_needed")

    result: Dict[str, Any] = {
        "fatigue_score": fatigue_score,
        "reasoning": gemini_decision.get("reasoning", []),
        "action_taken": action,
        "routine": None,
        "calendar_event": None,
    }

    if action == "intervention_scheduled":
        _log("decision", "🚨 Threshold exceeded — initiating autonomous intervention")

        targeted_areas = gemini_decision.get("targeted_areas", [])
        feedback = await db_svc.get_latest_feedback(db, user_id)
        exercises = _pick_exercises_by_areas(targeted_areas, feedback)
        title = gemini_decision.get("routine_title") or _generate_routine_title(fatigue_score, feedback)
        total_secs = sum(e.duration_secs for e in exercises)

        protocol = GeneratedProtocol(
            title=title,
            duration_mins=max(total_secs // 60, 5),
            movements=exercises,
        )

        slot_start = now + timedelta(minutes=random.randint(5, 30))
        slot_end = slot_start + timedelta(minutes=10)

        routine = OrchestratedRoutine(
            user_id=user_id,
            scheduled_timestamp=slot_start,
            associated_calendar_event_id=f"cal_evt_{random.randint(100000, 999999)}",
            status="scheduled",
            generated_protocol=protocol,
        )

        _log("action", f"📝 Generated routine: \"{title}\" — {len(exercises)} exercises, {protocol.duration_mins} min")
        await db_svc.insert_routine(db, routine)
        _log("action", "💾 Routine saved to MongoDB → orchestrated_routines collection")

        cal_event = {
            "user_id": user_id,
            "event_id": routine.associated_calendar_event_id,
            "title": f"ErgoFlow: {title}",
            "start_time": slot_start,
            "end_time": slot_end,
            "description": f"Auto-scheduled by Gemini agent. Fatigue score: {fatigue_score}/10",
            "status": "confirmed",
        }
        await db_svc.insert_calendar_event(db, cal_event)
        cal_event.pop("_id", None)
        _log("action", f"📅 Calendar event created: \"{cal_event['title']}\"",
             {"calendar_event_id": routine.associated_calendar_event_id})
        _log("result",
             f"✅ Intervention complete — Recovery scheduled at {slot_start.strftime('%H:%M')} UTC",
             {"fatigue_score": fatigue_score, "routine_title": title})

        result["action_taken"] = "intervention_scheduled"
        result["routine"] = routine.model_dump()
        result["calendar_event"] = cal_event
    else:
        _log("result",
             f"✅ No intervention needed — fatigue score {fatigue_score}/10 within acceptable range",
             {"fatigue_score": fatigue_score})

    result["reasoning"] = [e.message for e in activity_entries]
    await db_svc.insert_activities_bulk(db, activity_entries)
    return result
