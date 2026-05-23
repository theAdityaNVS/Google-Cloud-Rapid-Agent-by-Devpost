"""
ErgoFlow AI — Gemini Agent Service
Uses google-generativeai function calling to drive multi-step ergonomic assessment.
Gemini calls MCP tools to fetch MongoDB data, then reasons to produce a decision.
"""
from __future__ import annotations

import json
import logging
from typing import Any

import google.generativeai as genai

from app.config import settings
from app.services.mcp_client import mcp_find

logger = logging.getLogger("ergoflow")

SYSTEM_PROMPT = """You are ErgoFlow AI, an autonomous occupational health agent for software engineers.

Your job is to assess a user's ergonomic fatigue and decide whether to schedule a recovery routine.

Steps you MUST follow:
1. Call query_biometrics(user_id) to fetch the user's latest biometric telemetry
2. Call query_feedback(user_id) to fetch the user's latest subjective pain ratings
3. Compute a fatigue score 0-10 using these weights:
   - sitting_score = min(consecutive_sitting_mins / 120.0, 1.0) * 10
   - inactivity_score = max(1 - steps_count_today / 5000.0, 0) * 10
   - pain_score = avg(lower_back_stiffness, shoulder_tension, neck_pain) / 5.0 * 10
   - mental_score = avg(mental_fatigue, eye_strain) / 5.0 * 10
   - final = sitting_score*0.3 + pain_score*0.3 + inactivity_score*0.2 + mental_score*0.2
4. If final >= 6.0, set action="intervention_scheduled" and identify the 1-2 highest-scoring body areas
5. Return ONLY valid JSON — no markdown fences, no explanation outside the JSON

Required JSON schema (respond with ONLY this, no other text):
{
  "fatigue_score": <float, 0.0-10.0>,
  "reasoning": [
    "<step 1 description with numbers>",
    "<step 2 description with numbers>",
    "<step 3: fatigue calc with actual values>",
    "<step 4: intervention decision>"
  ],
  "action": "intervention_scheduled" | "no_action_needed",
  "routine_title": "<string, present only when action=intervention_scheduled>",
  "targeted_areas": ["lower_back" | "shoulder" | "neck" | "eyes" | "general"]
}"""


def _make_tools() -> list:
    return [
        genai.protos.Tool(
            function_declarations=[
                genai.protos.FunctionDeclaration(
                    name="query_biometrics",
                    description="Fetch the latest biometric telemetry document for a user from MongoDB",
                    parameters=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties={
                            "user_id": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="User ID to query, e.g. usr_dev_9981",
                            )
                        },
                        required=["user_id"],
                    ),
                ),
                genai.protos.FunctionDeclaration(
                    name="query_feedback",
                    description="Fetch the latest subjective pain and fatigue feedback for a user from MongoDB",
                    parameters=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties={
                            "user_id": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="User ID to query, e.g. usr_dev_9981",
                            )
                        },
                        required=["user_id"],
                    ),
                ),
            ]
        )
    ]


async def _dispatch_function(name: str, args: dict) -> str:
    """Execute a Gemini function call and return the JSON result string."""
    if name == "query_biometrics":
        docs = await mcp_find(
            collection="biometric_telemetry",
            filter_={"user_id": args["user_id"]},
            sort={"timestamp": -1},
            limit=1,
        )
        return json.dumps(docs[0] if docs else {}, default=str)

    if name == "query_feedback":
        docs = await mcp_find(
            collection="subjective_feedback",
            filter_={"user_id": args["user_id"]},
            sort={"timestamp": -1},
            limit=1,
        )
        return json.dumps(docs[0] if docs else {}, default=str)

    return json.dumps({"error": f"unknown function: {name}"})


async def run_agent(user_id: str) -> dict[str, Any]:
    """
    Run the Gemini agent for a user.
    Returns a dict with: fatigue_score, reasoning, action, routine_title, targeted_areas.
    Raises ValueError if Gemini key is not configured.
    """
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY not set — cannot run Gemini agent")

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(
        model_name=settings.gemini_model,
        tools=_make_tools(),
        system_instruction=SYSTEM_PROMPT,
    )
    chat = model.start_chat()

    response = chat.send_message(
        f"Evaluate ergonomic health for user ID: {user_id}"
    )

    # Tool-call loop — at most 4 rounds to avoid runaway loops
    for _ in range(4):
        parts = response.candidates[0].content.parts
        fn_calls = [p for p in parts if hasattr(p, "function_call") and p.function_call.name]
        if not fn_calls:
            break

        fn_responses = []
        for part in fn_calls:
            fc = part.function_call
            logger.info("Gemini calling tool: %s(%s)", fc.name, dict(fc.args))
            result_str = await _dispatch_function(fc.name, dict(fc.args))
            fn_responses.append(
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=fc.name,
                        response={"result": result_str},
                    )
                )
            )

        response = chat.send_message(fn_responses)

    # Parse the final JSON from Gemini's text response
    text = response.text.strip()
    # Strip markdown fences if model adds them despite instructions
    if "```" in text:
        text = text.split("```")[1].lstrip("json").strip()

    return json.loads(text)
