# Project Memory & Context (ErgoFlow AI)

This file serves as the long-term memory for AI agents working on this project. **AI Agents MUST read this file before beginning work and update it after completing tasks.**

## Project Overview
- **Name:** ErgoFlow AI
- **Goal:** Autonomous Context-Aware Occupational Health Agent for software engineers.
- **Spec:** See `IDEA.md` for full requirements and schemas.
- **Implementation Plan:** See `docs/implementation_plan.md` for detailed tier-based feature breakdown.
- **Hackathon Deadline:** June 11, 2026, 2:00 PM PDT
- **Track:** MongoDB ($10K prize pool)

## Tech Stack (Actual, Implemented)
| Layer | Technology |
|---|---|
| Frontend | Next.js 16 (App Router), React 19, Recharts 3, Vanilla CSS (dark theme) |
| Backend | Python 3.12, FastAPI 0.115, Motor 3.5 (async MongoDB), Pydantic 2.9 |
| Database | MongoDB Atlas (M0 free tier) — cluster: `ergoai.ofo6lhr.mongodb.net` |
| AI Agent | **SIMULATED** — local Python fatigue-scoring (needs Gemini 3 / Agent Builder swap) |
| Calendar | **MOCK** — events stored in MongoDB (needs Google Calendar OAuth2) |
| MCP Server | ✅ **DEPLOYED** — `https://ergoflow-mongodb-mcp-555089344520.us-central1.run.app` (Cloud Run, `theadityanvs-unified` project) |
| Deployment | LOCAL (backend+frontend) + MCP on Cloud Run |

## Current State (Last Updated: 2026-05-22T12:46 IST)

### Architecture Decisions Made
- **Stack Change**: Switched from Java/Spring Boot (IDEA.md) to **Python FastAPI** — FastAPI has native Google ADK support, faster iteration.
- **Frontend**: Chose Next.js over plain React/Vue for SSR, polished ecosystem.
- **Styling**: Vanilla CSS with CSS variables (glassmorphism dark theme) — NOT Tailwind.
- **Charts**: Recharts library for health trend visualization.
- **Database driver**: Motor (async) instead of PyMongo for non-blocking MongoDB access.

### What is Completed (Done) ✅
- **Frontend Dashboard (Next.js & React)**: Fully scaffolded and active UI containing:
  - Sidebar and Header navigation with tab routing (dashboard, agent, routines, calendar, analytics, settings).
  - Interactive components: `FatigueScoreCard`, `HealthTrendChart` (biometrics timeline via Recharts), `CalendarSyncStatus` (upcoming breaks), `AgentActivityFeed` (reasoning logs), `RoutineCard` (exercise protocols), and `MicroFeedbackModal` (qualitative muscle assessments).
  - Configured with automatic backend polling every 10 seconds and parallel API fetches.
  - Dark theme with CSS variables, glassmorphism cards, micro-animations, responsive design.
  - **22KB globals.css** design system with full color palette, transitions, and glassmorphism.
- **Backend Architecture (FastAPI & MongoDB)**: Fully structured backend featuring:
  - Lifespan MongoDB connection management via asynchronous **Motor** driver.
  - Structured routing: 7 routers (`/api/health`, `/api/telemetry`, `/api/feedback`, `/api/agent/routines`, `/api/agent`, `/api/calendar`, `/api/simulator`).
  - Strict Pydantic schemas: 5 models (UserProfile, BiometricTelemetry, SubjectiveFeedback, OrchestratedRoutine, AgentActivityEntry) + sub-models.
  - MongoDB indexes created on startup for all query patterns.
  - CORS configured for Next.js frontend (localhost:3000).
  - Full CRUD in `mongodb_service.py` for all 6 collections.
- **Mock Services / Demos**:
  - `simulator_service.py`: Generates complex biometric telemetry & user sentiment logs representing high-fatigue, moderate, or healthy workdays (3 scenarios, multi-day support).
  - `agent_service.py`: Emulates the cognitive pipeline — calculates composite fatigue scores (sitting 0.3 + pain 0.3 + inactivity 0.2 + mental 0.2 weighting), picks targeted exercises from a 12-exercise library, generates titled routines, creates mock calendar events, and logs all reasoning steps to `agent_activity_log`.
  - `calendar_service.py`: Stores mock calendar events in MongoDB with CRUD operations.
- **API Client (Frontend)**: `lib/api.ts` with typed fetch wrapper and endpoints for all backend routes.
- **TypeScript Types**: `lib/types.ts` with matching frontend type definitions.
- **Demo Screenshots**: `docs/screenshots/dashboard.png` and `docs/screenshots/api_docs.png` exist.
- **Memory Rules**: Created `.clinerules` and `.cursorrules` to force future AI agents to check and update project memory.
- **README.md**: Professional with mermaid architecture diagram, setup instructions, and overview.

### What is Simulated (Working but needs production swap) ⚠️
- **Agent Reasoning Pipeline** (`agent_service.py`): Fatigue scoring, exercise selection, routine generation — all local Python. The `_log()` calls simulate MCP tool calls with emoji-prefixed messages. Needs swap to real Gemini 3 API via Agent Builder or ADK.
- **Calendar Events** (`calendar_service.py`): Events stored in MongoDB `calendar_events` collection. Needs swap to actual Google Calendar API with OAuth2.

### What is Missing (Pending) ❌

#### Critical — Required for Hackathon Judging
1. **Google Cloud Agent Builder + Gemini 3 Integration** (Judging: "Multi-Step Planning"):
   - No Agent Builder, ADK, or Vertex AI code exists anywhere.
   - `config.py` has empty placeholder fields (`agent_builder_endpoint`, `agent_builder_api_key`).
   - Need to: Create agent in Agent Studio, register MongoDB MCP as tool, configure system prompt, call agent from backend.
   - **Est: 6-8 hours**

2. **MongoDB MCP Server** (Judging: "Partner Power" — MANDATORY):
   - ✅ **COMPLETED 2026-05-22**
   - Package `mongodb-mcp-server@1.11.0` deployed on Cloud Run (`theadityanvs-unified`)
   - **URL**: `https://ergoflow-mongodb-mcp-555089344520.us-central1.run.app`
   - Config: `MDB_MCP_TRANSPORT=http`, `MDB_MCP_READ_ONLY=true`, port 8080
   - 18 tools exposed: `find`, `aggregate`, `list-collections`, `collection-schema`, `count`, etc.
   - Files: `mcp-server/Dockerfile`, `mcp-server/package.json`, `mcp-server/.env.example`, `mcp-server/README.md`
   - **Next**: Register this URL in Agent Builder as an MCP Tool

3. **Google Calendar OAuth2 + Real API** (Judging: "Beyond Chat"):
   - `requirements.txt` does NOT include `google-api-python-client` or `google-auth-oauthlib`.
   - `.env` has empty `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.
   - Need to: Set up OAuth consent screen in Google Cloud, implement OAuth router, swap calendar_service.py.
   - **Est: 4-5 hours**

#### Important — For Demo Credibility
4. **Dockerfiles** (backend + frontend): Not created yet.
5. **Cloud Run Deployment**: No deploy configs or GitHub Actions workflows.
6. **Vercel Deployment**: No Vercel config for frontend.
7. **Demo Video** (3 min): Not recorded — required for submission.

#### Nice-to-Have (Tier 3)
8. Animated exercise illustrations (CSS/SVG stick figures)
9. Agent evaluation/observability metrics dashboard
10. Multi-user simulation support
11. Settings panel (currently shows "coming soon")

## MongoDB Collections
| Collection | Fields | Indexed |
|---|---|---|
| `user_profiles` | user_id, name, created_at, preferences | ✅ |
| `biometric_telemetry` | user_id, timestamp, metrics, context | ✅ (user_id + timestamp) |
| `subjective_feedback` | user_id, timestamp, assessments | ✅ (user_id + timestamp) |
| `orchestrated_routines` | user_id, scheduled_timestamp, status, generated_protocol | ✅ (user_id + scheduled_timestamp) |
| `agent_activity_log` | user_id, created_at, entry_type, message, metadata | ✅ (user_id + created_at) |
| `calendar_events` | user_id, event_id, title, start_time, end_time, status | ✅ |

## API Endpoints (Implemented)
| Method | Endpoint | Router | Status |
|---|---|---|---|
| GET | `/api/health/status` | health.py | ✅ |
| POST | `/api/telemetry/biometrics` | telemetry.py | ✅ |
| GET | `/api/telemetry/latest` | telemetry.py | ✅ |
| GET | `/api/telemetry/history` | telemetry.py | ✅ |
| POST | `/api/feedback/micro-prompt` | feedback.py | ✅ |
| GET | `/api/feedback/history` | feedback.py | ✅ |
| GET | `/api/agent/routines/next` | routines.py | ✅ |
| GET | `/api/agent/routines/history` | routines.py | ✅ |
| POST | `/api/agent/evaluate` | agent.py | ✅ (simulated) |
| GET | `/api/agent/activity` | agent.py | ✅ |
| GET | `/api/calendar/events` | calendar.py | ✅ (mock) |
| POST | `/api/simulator/generate` | simulator.py | ✅ |

## File Structure Summary
```
root/
├── IDEA.md                    # Full project spec and schemas
├── MEMORY.md                  # This file — AI agent context
├── README.md                  # Project README with architecture diagram
├── .cursorrules               # AI memory enforcement rules
├── .clinerules                # AI memory enforcement rules
├── docs/
│   ├── implementation_plan.md # Tiered implementation plan
│   ├── hackathon_research.md  # Hackathon rules and judging research
│   └── screenshots/           # Dashboard + API docs screenshots
├── backend/
│   ├── run.py                 # Uvicorn entry point
│   ├── requirements.txt       # Python dependencies
│   ├── .env / .env.example    # Environment config
│   └── app/
│       ├── main.py            # FastAPI app with CORS + lifespan
│       ├── config.py          # Pydantic settings
│       ├── database.py        # Motor async MongoDB connection
│       ├── models/            # 5 Pydantic models
│       ├── routers/           # 7 API routers
│       ├── services/          # 4 service modules
│       └── utils/seed_data.py # Demo seed data
└── frontend/
    ├── app/                   # Next.js App Router (page.tsx, layout.tsx, globals.css)
    ├── components/            # 9 React components in 5 directories
    ├── lib/                   # api.ts, types.ts, mockData.ts
    └── package.json           # Next.js 16 + React 19 + Recharts
```

---
*Note to AI Agents: Append new decisions, feature completions, and architectural changes below this line.*

### Change Log
- **2026-05-22 (audit)**: Full codebase audit performed. Documented all completed features, simulated services, and missing production integrations. Identified 4 critical blockers for hackathon submission. See project_status_report.md artifact for detailed analysis.
- **2026-05-22 (MCP deploy)**: MongoDB MCP Server deployed to Cloud Run. URL: `https://ergoflow-mongodb-mcp-555089344520.us-central1.run.app`. GCP project: `theadityanvs-unified`. Server responds with 18 tools (find, aggregate, list-collections, etc.) connected to Atlas cluster `ergoai.ofo6lhr.mongodb.net`. Critical blocker #2 (Partner Power) is now unblocked. Next: register URL in Agent Builder.
