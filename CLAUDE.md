# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: ErgoFlow AI

Autonomous Context-Aware Occupational Health Agent for software engineers. Hackathon deadline: **June 11, 2026, 2:00 PM PDT** (Google Cloud Rapid Agent / MongoDB track).

**Always read `MEMORY.md` before starting a task, but verify claims against actual code** — the audit below documents several discrepancies between MEMORY.md and reality.

---

## Commands

### Backend (Python / FastAPI)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # fill MONGODB_URI with Atlas URI
python run.py          # starts on http://localhost:8000 with hot-reload
```

Seed demo data (required before first use — also creates MongoDB indexes):

```powershell
cd backend
python -m app.utils.seed_data
```

API docs: `http://localhost:8000/docs`

### Frontend (Next.js)

```powershell
cd frontend
npm install
npm run dev    # starts on http://localhost:3000
npm run build
npm run lint
```

Set `NEXT_PUBLIC_API_URL` in `frontend/.env.local` when the backend is deployed (defaults to `localhost:8000`).

### MongoDB MCP Server (local test)

```powershell
$env:MDB_MCP_CONNECTION_STRING="mongodb+srv://admin:admin@ergoai.ofo6lhr.mongodb.net/?appName=ErgoAI"
$env:MDB_MCP_TRANSPORT="http"
$env:MDB_MCP_HTTP_HOST="0.0.0.0"
$env:MDB_MCP_HTTP_PORT="8080"
$env:MDB_MCP_READ_ONLY="true"
npx -y mongodb-mcp-server@latest
```

### MCP Server — redeploy to Cloud Run

```bash
cd mcp-server
gcloud run deploy ergoflow-mongodb-mcp \
  --source . --platform managed --region us-central1 \
  --allow-unauthenticated --port 8080 \
  --set-env-vars "MDB_MCP_TRANSPORT=http,MDB_MCP_HTTP_HOST=0.0.0.0,MDB_MCP_HTTP_PORT=8080,MDB_MCP_READ_ONLY=true" \
  --set-env-vars "MDB_MCP_CONNECTION_STRING=mongodb+srv://admin:admin@ergoai.ofo6lhr.mongodb.net/?appName=ErgoAI"
```

Deployed URL: `https://ergoflow-mongodb-mcp-555089344520.us-central1.run.app`

---

## Architecture

```
frontend (Next.js 16, React 19)
    └── polls backend every 10s via lib/api.ts
    └── single-tenant: hardcoded user_id = 'usr_dev_9981' (page.tsx:56)

backend (FastAPI 0.115, Python 3.12)
    ├── app/main.py          — CORS, lifespan, router registration
    ├── app/config.py        — pydantic-settings (Settings singleton)
    ├── app/database.py      — Motor async connection to MongoDB Atlas
    ├── app/models/          — 5 Pydantic v2 models + sub-models
    ├── app/routers/         — 7 routers: health, telemetry, feedback,
    │                          routines, agent, calendar, simulator
    └── app/services/
        ├── mongodb_service.py   — all CRUD for 6 Atlas collections
        ├── agent_service.py     — SIMULATED fatigue scoring + routine gen
        ├── simulator_service.py — generates biometric telemetry (3 scenarios)
        └── calendar_service.py  — mock calendar events stored in MongoDB

mcp-server/ (Node.js, mongodb-mcp-server@1.11.0)
    └── Deployed on Cloud Run — exposes Atlas read-only via HTTP MCP
    └── Currently has NO consumer — agent_service.py does not call it
    └── Intended future role: registered as Tool in Agent Builder
```

### Key data flow

1. `page.tsx` loads → auto-triggers `agentApi.evaluate()` if activity feed is empty (first-run bootstrap).
2. `POST /api/agent/evaluate` → `agent_service.evaluate_user()` reads Atlas for latest telemetry + feedback, runs weighted formula, if score ≥ 6 generates a routine + MongoDB calendar event, saves all activity logs.
3. Frontend polls every 10s and renders: `FatigueScoreCard`, `HealthTrendChart`, `AgentActivityFeed`, `RoutineCard`, `CalendarSyncStatus`.
4. On feedback submit → `feedbackApi.submit()` → immediately triggers `evaluate()` again to re-score.

### What is simulated vs. real (verified by code audit)

| Component | Status | Key file |
|---|---|---|
| MongoDB Atlas reads/writes | **REAL** | `services/mongodb_service.py` |
| Fatigue scoring | **SIMULATED** — hardcoded weighted formula | `agent_service.py:71-105` |
| Exercise selection | **SIMULATED** — `random.choice()` from static library | `agent_service.py:108-136` |
| MCP tool calls in activity log | **FAKE** — emoji strings, not real MCP calls | `agent_service.py:183-184` |
| Calendar slot selection | **FAKE** — `now + random.randint(5,30)` minutes | `agent_service.py:234` |
| Calendar events | **MOCK** — MongoDB documents only, not Google Calendar | `calendar_service.py` |
| Gemini / Agent Builder | **NOT IMPLEMENTED** — zero AI libraries in requirements.txt | `requirements.txt` |
| `/api/health/gemini` status | **MISLEADING** — reports "configured" if env var exists, no API call | `routers/health.py:26-35` |

### Known bugs / gaps found in audit (not in MEMORY.md)

- **Indexes not created on startup**: `ensure_indexes()` is only called from `seed_data.py`, never from `main.py` lifespan. Fresh deployments have no indexes until seed is run. Fix: call `await ensure_indexes(get_database())` inside `main.py` lifespan after `connect_to_mongo()`.
- **`settings.mcp_server_url` is unused**: `config.py:31-34` declares the field but no service reads it. The MCP server is deployed but disconnected from the FastAPI app.
- **`frontend/lib/mockData.ts` is dead code**: zero imports anywhere; can be deleted or repurposed as demo fallback.
- **`mcp-server/node_modules/` is committed to git**: significant repo bloat; add to `.gitignore`.
- **MEMORY.md endpoint table is incomplete**: `GET /api/feedback/latest` exists at `routers/feedback.py:32-41` but is not documented.
- **`user_profiles` and `calendar_events` collections have no indexes** — `ensure_indexes()` only covers the other 4.

### Configuration

Settings in `backend/app/config.py` load from `backend/.env`:
- `MONGODB_URI` — Atlas connection string
- `GOOGLE_CLOUD_PROJECT`, `AGENT_BUILDER_ENDPOINT` — empty placeholders for future Agent Builder
- `MCP_SERVER_URL` — deployed Cloud Run URL (declared but currently unused by any code)
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` — empty, Calendar OAuth not implemented

### Frontend styling

Vanilla CSS only — no Tailwind. All design tokens in `frontend/app/globals.css` (22KB). CSS class conventions: `glass-card`, `stat-card`, `btn btn-secondary`, `animate-fade-in`, `text-critical` / `text-calm` / `text-warning`.

---

## Hackathon next steps (ranked by judging impact)

### 1. Google Cloud Agent Builder + Gemini — CRITICAL (~6-8 hrs)
The judging differentiator. Without it the project is a simulation, not an AI agent.
- Create agent in Agent Studio, register MCP URL as tool `mongodb-ergoflow`
- Add `google-cloud-aiplatform` or `google-genai` to `requirements.txt`
- Replace `agent_service.evaluate_user()` body with a Gemini API call; keep existing MongoDB writes so frontend pipeline stays intact
- Write system prompt instructing Gemini to query MCP for telemetry/feedback, compute fatigue, decide intervention

### 2. Fix `ensure_indexes()` on startup — EASY WIN (~15 min)
In `backend/app/main.py:21`, after `await connect_to_mongo()`:
```python
from app.services.mongodb_service import ensure_indexes
await ensure_indexes(get_database())
```

### 3. Google Calendar OAuth2 — MEDIUM (~4-5 hrs)
- Add `google-api-python-client` + `google-auth-oauthlib` to `requirements.txt`
- Add OAuth router at `/auth/google` + `/auth/callback`
- Replace `calendar_service.create_event()` with real `service.events().insert()`

### 4. Dockerfiles + deployment configs — REQUIRED FOR DEMO (~1-2 hrs)
`backend/Dockerfile`: python:3.12-slim, copy requirements, `CMD uvicorn app.main:app --host 0.0.0.0 --port 8080`
`frontend/Dockerfile`: node:22-alpine, npm ci + build, `CMD next start`

### 5. Add `.gitignore` entry for `mcp-server/node_modules/` — 5 min
