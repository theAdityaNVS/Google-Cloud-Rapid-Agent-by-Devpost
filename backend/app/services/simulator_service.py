"""
ErgoFlow AI — Realistic Data Simulator
Generates believable time-series biometric and feedback data for demos.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Literal

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models import (
    BiometricTelemetry, TelemetryMetrics, TelemetryContext,
    SubjectiveFeedback, FeedbackAssessments,
)
from app.services import mongodb_service as db_svc


Scenario = Literal["high_fatigue", "moderate", "healthy"]


def _generate_telemetry_series(
    user_id: str,
    scenario: Scenario,
    start_time: datetime,
    hours: int = 8,
) -> List[BiometricTelemetry]:
    """Generate telemetry entries every 30 mins for a work day."""
    entries: List[BiometricTelemetry] = []
    interval_mins = 30
    num_points = (hours * 60) // interval_mins

    cumulative_steps = 0
    cumulative_stand = 0.0
    sitting_streak = 0

    for i in range(num_points):
        ts = start_time + timedelta(minutes=i * interval_mins)
        progress = i / max(num_points - 1, 1)  # 0.0 → 1.0 through the day

        if scenario == "high_fatigue":
            # Long sitting, few steps, declining HRV
            steps_delta = random.randint(5, 40)
            stood_up = random.random() < 0.1  # 10% chance of standing
            hrv = max(25, 55 - progress * 30 + random.uniform(-3, 3))
            calories = int(80 + progress * 40 + random.uniform(-10, 10))
            sitting_streak += interval_mins if not stood_up else 0
            if stood_up:
                sitting_streak = 0
                cumulative_stand += 0.5
            cal_state = "in_deep_focus_block" if random.random() < 0.7 else "in_meeting"

        elif scenario == "moderate":
            steps_delta = random.randint(30, 150)
            stood_up = random.random() < 0.35
            hrv = 45 + random.uniform(-5, 5)
            calories = int(120 + progress * 80 + random.uniform(-15, 15))
            sitting_streak += interval_mins if not stood_up else 0
            if stood_up:
                sitting_streak = max(0, sitting_streak - 30)
                cumulative_stand += 0.5
            cal_state = random.choice(["in_deep_focus_block", "free", "in_meeting"])

        else:  # healthy
            steps_delta = random.randint(100, 400)
            stood_up = random.random() < 0.6
            hrv = 60 + random.uniform(-5, 8)
            calories = int(180 + progress * 120 + random.uniform(-20, 20))
            sitting_streak += interval_mins if not stood_up else 0
            if stood_up:
                sitting_streak = 0
                cumulative_stand += 0.5
            cal_state = random.choice(["free", "in_deep_focus_block"])

        cumulative_steps += steps_delta

        entries.append(BiometricTelemetry(
            user_id=user_id,
            timestamp=ts,
            metrics=TelemetryMetrics(
                stand_hours_today=round(cumulative_stand, 1),
                active_calories_burned=calories,
                steps_count_today=cumulative_steps,
                heart_rate_variability_hrv_ms=round(hrv, 1),
            ),
            context=TelemetryContext(
                current_calendar_state=cal_state,
                consecutive_sitting_mins=sitting_streak,
            ),
        ))

    return entries


def _generate_feedback_entries(
    user_id: str,
    scenario: Scenario,
    start_time: datetime,
    hours: int = 8,
) -> List[SubjectiveFeedback]:
    """Generate 2-4 feedback entries spread across the day."""
    entries: List[SubjectiveFeedback] = []
    count = random.randint(2, 4)

    for i in range(count):
        offset_mins = random.randint(60, hours * 60 - 30)
        ts = start_time + timedelta(minutes=offset_mins)
        progress = offset_mins / (hours * 60)

        if scenario == "high_fatigue":
            base = 3 + progress * 1.5
            back = min(5, int(base + random.uniform(-0.5, 1)))
            shoulder = min(5, int(base + random.uniform(-1, 0.5)))
            neck = min(5, int(base + random.uniform(-1, 1)))
            eyes = min(5, int(base + random.uniform(-0.5, 0.5)))
            mental = min(5, int(base + random.uniform(-0.5, 1)))
        elif scenario == "moderate":
            back = random.randint(2, 3)
            shoulder = random.randint(1, 3)
            neck = random.randint(1, 3)
            eyes = random.randint(2, 3)
            mental = random.randint(2, 3)
        else:
            back = random.randint(1, 2)
            shoulder = random.randint(1, 2)
            neck = random.randint(1, 1)
            eyes = random.randint(1, 2)
            mental = random.randint(1, 2)

        entries.append(SubjectiveFeedback(
            user_id=user_id,
            timestamp=ts,
            assessments=FeedbackAssessments(
                lower_back_stiffness=max(1, back),
                shoulder_tension=max(1, shoulder),
                neck_pain=max(1, neck),
                eye_strain=max(1, eyes),
                mental_fatigue=max(1, mental),
            ),
        ))

    entries.sort(key=lambda x: x.timestamp)
    return entries


async def generate_scenario(
    db: AsyncIOMotorDatabase,
    user_id: str,
    scenario: Scenario,
    days: int = 1,
) -> Dict:
    """Generate a full scenario's worth of data and insert into MongoDB."""
    total_telemetry = 0
    total_feedback = 0

    for day_offset in range(days):
        day_start = datetime.now(timezone.utc).replace(
            hour=9, minute=0, second=0, microsecond=0
        ) - timedelta(days=days - 1 - day_offset)

        # Generate and insert telemetry
        telemetry_entries = _generate_telemetry_series(
            user_id, scenario, day_start, hours=10
        )
        for entry in telemetry_entries:
            await db_svc.insert_telemetry(db, entry)
        total_telemetry += len(telemetry_entries)

        # Generate and insert feedback
        feedback_entries = _generate_feedback_entries(
            user_id, scenario, day_start, hours=10
        )
        for entry in feedback_entries:
            await db_svc.insert_feedback(db, entry)
        total_feedback += len(feedback_entries)

    return {
        "scenario": scenario,
        "days": days,
        "telemetry_entries": total_telemetry,
        "feedback_entries": total_feedback,
        "user_id": user_id,
    }
