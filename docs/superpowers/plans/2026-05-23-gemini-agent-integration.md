# Gemini Agent Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the simulated Python fatigue-scoring pipeline in `agent_service.py` with a real Gemini LLM agent that uses the deployed MongoDB MCP server (Cloud Run) as its data source, turning ErgoFlow AI into a genuine AI agent for the hackathon judges.

**Architecture:** Gemini (via `google-generativeai` SDK) receives a prompt to evaluate a user's ergonomic health. It uses function-calling tools backed by HTTP requests to the deployed MCP server on Cloud Run, which reads MongoDB Atlas. Gemini reasons through the data, decides on an intervention, and returns structured JSON. The existing MongoDB write pipeline (routines, calendar events, activity log) stays intact.

**Tech Stack:** `google-generativeai`, `httpx` (async HTTP for MCP calls), FastAPI (existing), MongoDB Atlas + Motor (existing), MongoDB MCP Server on Cloud Run (already deployed at `https://ergoflow-mongodb-mcp-555089344520.us-central1.run.app`)

---

## Current State Checklist

| Item | Status |
|---|---|
| MongoDB MCP Server on Cloud Run | ✅ LIVE — verified via initialize handshake |
| MCP server URL in config.py | ✅ Declared — but nothing reads it yet |
| Agent pipeline in agent_service.py | ⚠️ Simulated local Python — no LLM |
| google-generativeai in requirements.txt | ❌ Missing |
| httpx in requirements.txt | ❌ Missing |
| GEMINI_API_KEY in config / .env.example | ❌ Missing |
| ensure_indexes() called on startup | ❌ Only runs from seed_data.py |
| Backend Dockerfile | ❌ Missing |
| Frontend Dockerfile | ❌ Missing |

---

## Phase A — Quick Fixes (30 min)

### Task 1: Fix `ensure_indexes()` on startup

**Files:**
- Modify: `backend/app/main.py`

- [ ] **Step 1: Add `ensure_indexes` call to the lifespan context manager**

In `backend/app/main.py`, replace the lifespan function (lines 17–25):

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    try:
        await connect_to_mongo()
        from app.services.mongodb_service import ensure_indexes
        await ensure_indexes(get_database())
    except Exception as e:
        logger.warning("MongoDB not available (%s). Endpoints requiring DB will return 503.", e)
    yield
    await close_mongo_connection()
```

- [ ] **Step 2: Verify by running the backend and checking logs**

```powershell
cd backend
.\venv\Scripts\activate
python run.py
```

Expected log output on startup (no error, no "MongoDB not available" warning):
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/main.py
git commit -m "fix: call ensure_indexes on app startup"
```

---

## Phase B — Gemini Agent Integration (6–8 hrs)

### Task 2: Add dependencies

**Files:**
- Modify: `backend/requirements.txt`

- [ ] **Step 1: Add google-generativeai and httpx to requirements.txt**

Append to `backend/requirements.txt`:
```
google-generativeai==0.8.3
httpx==0.27.2
```

- [ ] **Step 2: Install in virtualenv**

```powershell
cd backend
.\venv\Scripts\activate
pip install google-generativeai==0.8.3 httpx==0.27.2
```

Expected: Both packages install without errors.

- [ ] **Step 3: Commit**

```bash
git add backend/requirements.txt
git commit -m "feat: add google-generativeai and httpx dependencies"
```

---

### Task 3: Add Gemini config to Settings

**Files:**
- Modify: `backend/app/config.py`
- Modify: `backend/.env.example`

- [ ] **Step 1: Add `gemini_api_key` field to the Settings class**

In `backend/app/config.py`, add after the `mcp_server_url` field (after line 34):

```python
    # ── Gemini API ───────────────────────────────────────────────────────────
    gemini_api_key: str = Field(default="", description="Google AI Studio API key for Gemini")
    gemini_model: str = Field(default="gemini-1.5-flash", description="Gemini model name")
```

- [ ] **Step 2: Add to .env.example**

Append to `backend/.env.example`:
```
# Gemini API (get key from https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-1.5-flash
```

- [ ] **Step 3: Add actual key to backend/.env (NOT committed)**

```powershell
# In backend/.env, add:
GEMINI_API_KEY=<your key from aistudio.google.com>
```

> Get a free API key at https://aistudio.google.com/app/apikey — free tier is sufficient for demo.

- [ ] **Step 4: Verify settings loads key**

```powershell
cd backend
.\venv\Scripts\activate
python -c "from app.config import settings; print('Key set:', bool(settings.gemini_api_key))"
```

Expected: `Key set: True`

- [ ] **Step 5: Commit**

```bash
git add backend/app/config.py backend/.env.example
git commit -m "feat: add Gemini API key config"
```

---

### Task 4: Create the MCP HTTP client

**Files:**
- Create: `backend/app/services/mcp_client.py`

The MCP server is already live at `https://ergoflow-mongodb-mcp-555089344520.us-central1.run.app`. It uses HTTP SSE transport. Each POST to `/mcp` returns a `text/event-stream` response where the result is on a `data:` line.

- [ ] **Step 1: Create `backend/app/services/mcp_client.py`**

```python
"""
ErgoFlow AI — MongoDB MCP HTTP Client
Makes JSON-RPC calls to the deployed mongodb-mcp-server on Cloud Run.
"""
from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger("ergoflow")

# Fall back to hardcoded URL if config not set
_MCP_BASE = (
    settings.mcp_server_url
    or "https://ergoflow-mongodb-mcp-555089344520.us-central1.run.app"
)


async def _mcp_request(method: str, params: dict, req_id: int = 1) -> dict:
    """Send a single MCP JSON-RPC request and parse the SSE response."""
    payload = {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params}
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(
            f"{_MCP_BASE}/mcp",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
        )
        resp.raise_for_status()
        for line in resp.text.splitlines():
            if line.startswith("data:"):
                return json.loads(line[5:].strip())
    return {}


def _extract_text_content(raw: dict) -> Any:
    """Pull the text content out of an MCP tools/call response."""
    content = raw.get("result", {}).get("content", [])
    if content and content[0].get("type") == "text":
        try:
            return json.loads(content[0]["text"])
        except json.JSONDecodeError:
            return content[0]["text"]
    return None


async def mcp_find(
    collection: str,
    filter_: dict,
    sort: dict | None = None,
    limit: int = 5,
) -> list:
    """Query a MongoDB collection via the MCP 'find' tool."""
    args: dict = {"collection": collection, "filter": filter_, "limit": limit}
    if sort:
        args["sort"] = sort
    raw = await _mcp_request("tools/call", {"name": "find", "arguments": args})
    result = _extract_text_content(raw)
    if isinstance(result, list):
        return result
    if isinstance(result, dict) and "documents" in result:
        return result["documents"]
    return []
```

- [ ] **Step 2: Smoke-test the client against the live server**

```powershell
cd backend
.\venv\Scripts\activate
python -c "
import asyncio
from app.services.mcp_client import mcp_find
result = asyncio.run(mcp_find('biometric_telemetry', {'user_id': 'usr_dev_9981'}, sort={'timestamp': -1}, limit=1))
print('Result:', result)
"
```

Expected: Either a dict with telemetry data (if seed was run), or an empty list `[]`.

If you get an empty list and no seed data exists yet, run the seed first:
```powershell
python -m app.utils.seed_data
```
Then retry the smoke test — you should see a telemetry document.

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/mcp_client.py
git commit -m "feat: add async MCP HTTP client for Cloud Run server"
```

---

### Task 5: Create the Gemini agent service

**Files:**
- Create: `backend/app/services/gemini_agent.py`

- [ ] **Step 1: Create `backend/app/services/gemini_agent.py`**

```python
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
        return json.dumps(docs[0] if docs else {})

    if name == "query_feedback":
        docs = await mcp_find(
            collection="subjective_feedback",
            filter_={"user_id": args["user_id"]},
            sort={"timestamp": -1},
            limit=1,
        )
        return json.dumps(docs[0] if docs else {})

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
```

- [ ] **Step 2: Smoke-test the agent directly**

```powershell
cd backend
.\venv\Scripts\activate
python -c "
import asyncio
from app.services.gemini_agent import run_agent
result = asyncio.run(run_agent('usr_dev_9981'))
import json; print(json.dumps(result, indent=2))
"
```

Expected output (values will vary):
```json
{
  "fatigue_score": 7.2,
  "reasoning": [
    "Queried biometric_telemetry: 127 sitting mins, 1240 steps, HRV 52ms",
    "Queried subjective_feedback: back=4/5, shoulder=3/5, neck=2/5, eyes=3/5",
    "Computed: sitting=10.0*0.3 + pain=6.0*0.3 + inactivity=7.5*0.2 + mental=6.0*0.2 = 7.5",
    "Score 7.5 >= 6.0 — scheduling intervention targeting lower_back and shoulder"
  ],
  "action": "intervention_scheduled",
  "routine_title": "Developer Lumbar & Shoulder Recovery Protocol",
  "targeted_areas": ["lower_back", "shoulder"]
}
```

If you get a JSON parse error, check `response.text` — the model may need a stricter system prompt. The system prompt already says "ONLY valid JSON", but if needed add `response_mime_type="application/json"` in the model config.

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/gemini_agent.py
git commit -m "feat: add Gemini function-calling agent with MCP tool integration"
```

---

### Task 6: Wire Gemini agent into `agent_service.py`

**Files:**
- Modify: `backend/app/services/agent_service.py`

The existing `evaluate_user()` function does the right MongoDB writes — we keep all of that. We replace only the scoring/decision logic (lines 161–296) with a Gemini call, falling back to simulation if the key isn't set.

- [ ] **Step 1: Add Gemini call with fallback at the top of `evaluate_user()`**

Replace the entire `evaluate_user` function body in `backend/app/services/agent_service.py`:

```python
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
            # Log each Gemini reasoning step as individual activity entries
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

    # If intervention needed, generate routine using targeted areas from Gemini
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
```

- [ ] **Step 2: Add the `_pick_exercises_by_areas` helper** (replaces `_pick_exercises` with explicit area list from Gemini)

Add this function after `_pick_exercises` in `agent_service.py`:

```python
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
```

- [ ] **Step 3: Test the full evaluate endpoint**

Start the backend and call the agent endpoint:
```powershell
# Terminal 1 — start backend
cd backend && .\venv\Scripts\activate && python run.py

# Terminal 2 — call agent
curl -X POST http://localhost:8000/api/agent/evaluate `
  -H "Content-Type: application/json" `
  -d '{"user_id": "usr_dev_9981"}'
```

Expected response has non-zero `fatigue_score`, `reasoning` is a list of strings from Gemini, and `action_taken` is either `"intervention_scheduled"` or `"no_action_needed"`.

Check the backend terminal logs — you should see:
```
INFO: Gemini calling tool: query_biometrics({'user_id': 'usr_dev_9981'})
INFO: Gemini calling tool: query_feedback({'user_id': 'usr_dev_9981'})
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/agent_service.py
git commit -m "feat: integrate Gemini agent into evaluate_user with MCP tool calls"
```

---

### Task 7: Fix the `/api/health/gemini` status endpoint

**Files:**
- Modify: `backend/app/routers/health.py`

- [ ] **Step 1: Replace the misleading health check with a real API probe**

Replace the `gemini_status` function in `backend/app/routers/health.py`:

```python
@router.get("/gemini")
async def gemini_status():
    from app.config import settings
    if not settings.gemini_api_key:
        return {
            "service": "gemini_agent",
            "mode": "simulated",
            "status": "no_api_key",
            "ready": False,
        }
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)
        resp = model.generate_content("ping")
        return {
            "service": "gemini_agent",
            "mode": "live",
            "model": settings.gemini_model,
            "status": "healthy",
            "ready": True,
        }
    except Exception as exc:
        return {
            "service": "gemini_agent",
            "mode": "live",
            "status": "error",
            "error": str(exc),
            "ready": False,
        }
```

- [ ] **Step 2: Verify**

```powershell
curl http://localhost:8000/api/health/gemini
```

Expected (with key set): `{"service":"gemini_agent","mode":"live","model":"gemini-1.5-flash","status":"healthy","ready":true}`

- [ ] **Step 3: Commit**

```bash
git add backend/app/routers/health.py
git commit -m "fix: health/gemini endpoint now makes a real API probe"
```

---

## Phase C — Dockerfiles (1–2 hrs)

### Task 8: Backend Dockerfile

**Files:**
- Create: `backend/Dockerfile`
- Create: `backend/.dockerignore`

- [ ] **Step 1: Create `backend/Dockerfile`**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY run.py .

ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

- [ ] **Step 2: Create `backend/.dockerignore`**

```
venv/
__pycache__/
*.pyc
.env
.env.*
!.env.example
```

- [ ] **Step 3: Build and test locally**

```powershell
cd backend
docker build -t ergoflow-backend .
docker run -p 8080:8080 `
  -e MONGODB_URI="mongodb+srv://admin:admin@ergoai.ofo6lhr.mongodb.net/?appName=ErgoAI" `
  -e GEMINI_API_KEY="<your-key>" `
  ergoflow-backend
```

Expected: Backend accessible at `http://localhost:8080/docs`

- [ ] **Step 4: Commit**

```bash
git add backend/Dockerfile backend/.dockerignore
git commit -m "feat: add backend Dockerfile for Cloud Run deployment"
```

---

### Task 9: Frontend Dockerfile

**Files:**
- Create: `frontend/Dockerfile`
- Create: `frontend/.dockerignore`

- [ ] **Step 1: Create `frontend/Dockerfile`**

```dockerfile
FROM node:22-alpine AS builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["node", "server.js"]
```

- [ ] **Step 2: Enable standalone output in Next.js config**

In `frontend/next.config.ts`, add the `output` field:

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
};

export default nextConfig;
```

- [ ] **Step 3: Create `frontend/.dockerignore`**

```
node_modules/
.next/
.env
.env.*
!.env.example
```

- [ ] **Step 4: Build and test**

```powershell
cd frontend
docker build --build-arg NEXT_PUBLIC_API_URL=http://localhost:8080 -t ergoflow-frontend .
docker run -p 3000:3000 ergoflow-frontend
```

Expected: Frontend at `http://localhost:3000`

- [ ] **Step 5: Commit**

```bash
git add frontend/Dockerfile frontend/.dockerignore frontend/next.config.ts
git commit -m "feat: add frontend Dockerfile with standalone Next.js build"
```

---

### Task 10: Deploy backend to Cloud Run

**Files:**
- No new files — uses existing `backend/Dockerfile`

> **Prerequisite:** `gcloud` CLI installed and authenticated (`gcloud auth login`). GCP project `theadityanvs-unified` already has Cloud Run enabled (used for MCP server).

- [ ] **Step 1: Deploy from backend/ directory**

```bash
cd backend
gcloud run deploy ergoflow-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars "MONGODB_URI=mongodb+srv://admin:admin@ergoai.ofo6lhr.mongodb.net/?appName=ErgoAI" \
  --set-env-vars "GEMINI_API_KEY=<your-key>" \
  --set-env-vars "MCP_SERVER_URL=https://ergoflow-mongodb-mcp-555089344520.us-central1.run.app"
```

- [ ] **Step 2: Get the deployed backend URL**

```bash
gcloud run services describe ergoflow-backend --region us-central1 --format 'value(status.url)'
```

Save this URL — it will be something like `https://ergoflow-backend-XXXX-uc.a.run.app`.

- [ ] **Step 3: Set frontend to point at deployed backend**

Create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=https://ergoflow-backend-XXXX-uc.a.run.app
```

- [ ] **Step 4: Verify backend health on Cloud Run**

```bash
curl https://ergoflow-backend-XXXX-uc.a.run.app/api/health/status
curl https://ergoflow-backend-XXXX-uc.a.run.app/api/health/gemini
```

Both should return `"ready": true`.

---

## Phase D — Optional: Google Calendar OAuth2 (4–5 hrs)

Only implement if Phase B is fully working and time permits. Required for the "Beyond Chat" judging criterion.

### Task 11: Real Google Calendar Integration

**Files:**
- Modify: `backend/requirements.txt`
- Modify: `backend/app/config.py`
- Create: `backend/app/routers/auth.py`
- Modify: `backend/app/services/calendar_service.py`

- [ ] **Step 1: Add OAuth dependencies**

Append to `backend/requirements.txt`:
```
google-api-python-client==2.151.0
google-auth-oauthlib==1.2.1
google-auth-httplib2==0.2.0
```

Install: `pip install google-api-python-client==2.151.0 google-auth-oauthlib==1.2.1 google-auth-httplib2==0.2.0`

- [ ] **Step 2: Add token storage config to Settings**

In `backend/app/config.py`, add after `google_redirect_uri`:
```python
    token_store_path: str = Field(
        default="token.json",
        description="Path to store Google OAuth tokens"
    )
```

- [ ] **Step 3: Create OAuth router `backend/app/routers/auth.py`**

```python
"""Google Calendar OAuth2 flow."""
import json
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from app.config import settings

router = APIRouter()
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def _get_flow() -> Flow:
    client_config = {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uris": [settings.google_redirect_uri],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    return Flow.from_client_config(client_config, scopes=SCOPES,
                                   redirect_uri=settings.google_redirect_uri)


@router.get("/google")
async def auth_start():
    flow = _get_flow()
    auth_url, _ = flow.authorization_url(prompt="consent")
    return RedirectResponse(auth_url)


@router.get("/callback")
async def auth_callback(code: str, state: str = ""):
    flow = _get_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials
    Path(settings.token_store_path).write_text(creds.to_json())
    return {"status": "authenticated", "message": "Google Calendar connected"}
```

- [ ] **Step 4: Register auth router in `main.py`**

Add in `backend/app/main.py` alongside other router imports:
```python
from app.routers import auth
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
```

- [ ] **Step 5: Replace `calendar_service.py` with real Calendar API**

Replace the entire content of `backend/app/services/calendar_service.py`:

```python
"""Google Calendar integration — real API when credentials exist, MongoDB mock otherwise."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from app.config import settings

logger = logging.getLogger("ergoflow")


def _get_calendar_service():
    """Return an authenticated Google Calendar service, or None if not credentialed."""
    token_path = Path(settings.token_store_path)
    if not token_path.exists():
        return None
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        creds = Credentials.from_authorized_user_info(
            json.loads(token_path.read_text()),
            scopes=["https://www.googleapis.com/auth/calendar.events"]
        )
        return build("calendar", "v3", credentials=creds)
    except Exception as exc:
        logger.warning("Google Calendar service unavailable: %s", exc)
        return None


async def create_calendar_event(title: str, start: datetime, end: datetime, description: str = "") -> dict:
    """Create a Google Calendar event, falling back to mock if not authenticated."""
    svc = _get_calendar_service()
    if svc:
        event = {
            "summary": title,
            "description": description,
            "start": {"dateTime": start.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": end.isoformat(), "timeZone": "UTC"},
        }
        created = svc.events().insert(calendarId="primary", body=event).execute()
        return {"event_id": created["id"], "html_link": created.get("htmlLink"), "source": "google_calendar"}
    return {"event_id": f"mock_{start.timestamp():.0f}", "source": "mock"}
```

- [ ] **Step 6: Set up OAuth in Google Cloud Console**

1. Go to https://console.cloud.google.com/apis/credentials
2. Create OAuth 2.0 Client ID (Web Application)
3. Add `http://localhost:8000/auth/callback` as Authorized Redirect URI
4. Copy Client ID and Secret into `backend/.env`:
   ```
   GOOGLE_CLIENT_ID=<your-client-id>
   GOOGLE_CLIENT_SECRET=<your-client-secret>
   ```
5. Visit `http://localhost:8000/auth/google` to complete the OAuth flow

- [ ] **Step 7: Commit**

```bash
git add backend/requirements.txt backend/app/config.py backend/app/routers/auth.py backend/app/services/calendar_service.py backend/app/main.py
git commit -m "feat: Google Calendar OAuth2 and real calendar event creation"
```

---

## Quick Reference — Verified Current State

| Service | URL | Status |
|---|---|---|
| MongoDB MCP Server | `https://ergoflow-mongodb-mcp-555089344520.us-central1.run.app` | ✅ LIVE |
| Backend (local) | `http://localhost:8000` | Run `python run.py` |
| Frontend (local) | `http://localhost:3000` | Run `npm run dev` |
| Atlas Cluster | `ergoai.ofo6lhr.mongodb.net` | ✅ Connected |
| Gemini Agent | — | ❌ Needs API key + Task 5 |

## Execution Order Summary

```
Task 1  → fix ensure_indexes                  (15 min)
Task 2  → add dependencies                    (5 min)
Task 3  → add Gemini config                   (10 min)
Task 4  → mcp_client.py + smoke test          (30 min)
Task 5  → gemini_agent.py + smoke test        (90 min)
Task 6  → wire into agent_service.py + test   (60 min)
Task 7  → fix health endpoint                 (15 min)
Task 8  → backend Dockerfile                  (30 min)
Task 9  → frontend Dockerfile                 (30 min)
Task 10 → deploy backend to Cloud Run         (45 min)
Task 11 → Google Calendar OAuth (optional)    (4-5 hrs)
─────────────────────────────────────────────
Total (Tasks 1-10):  ~6 hrs
Total (all):         ~10-11 hrs
```
