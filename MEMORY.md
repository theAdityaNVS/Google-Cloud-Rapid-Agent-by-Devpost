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
| Backend | Python 3.12, FastAPI 0.115, Motor 3.5 (async MongoDB), Pydantic 2.9, **google-generativeai 0.8** |
| Database | MongoDB Atlas (M0 free tier) — cluster: `ergoai.ofo6lhr.mongodb.net` |
| AI Agent | ✅ **IMPLEMENTED** — Gemini 1.5 Flash via SDK with Function Calling + MCP Tool Integration |
| Calendar | **MOCK** — events stored in MongoDB (needs Google Calendar OAuth2) |
| MCP Server | ✅ **DEPLOYED** — `https://ergoflow-mongodb-mcp-555089344520.us-central1.run.app` |
| Deployment | LOCAL (ready for Cloud Run/Vercel with Docker) |

## Current State (Last Updated: 2026-05-25T11:00 IST)

### Architecture Decisions Made
- **Stack Change**: Switched from Java/Spring Boot (IDEA.md) to **Python FastAPI** — FastAPI has native Google ADK support, faster iteration.
- **AI Implementation**: Chose **google-generativeai SDK** with manual function calling over Vertex AI Agent Builder UI for better programmatic control and local testing.
- **MCP Communication**: Implemented a custom **JSON-RPC HTTP client** (`mcp_client.py`) to bridge FastAPI with the Cloud Run-hosted MCP server.
- **Frontend**: Chose Next.js over plain React/Vue for SSR, polished ecosystem.
- **Styling**: Vanilla CSS with CSS variables (glassmorphism dark theme) — NOT Tailwind.
- **Charts**: Recharts library for health trend visualization.

### What is Completed (Done) ✅
- **Gemini Agent Integration (`gemini_agent.py`)**: Real AI cognitive pipeline implemented:
  - Uses Gemini 1.5 Flash with function calling capabilities.
  - Dynamically calls tools to query MongoDB for latest biometrics and feedback.
  - Implements complex fatigue scoring logic (reasoning steps: 0-10 scale).
  - Generates targeted routine titles and identifies specific body areas for intervention.
  - Integrated into the `/api/agent/evaluate` endpoint with a local fallback mechanism.
- **MongoDB MCP Client (`mcp_client.py`)**: Custom bridge to the deployed MCP server:
  - Handles MCP protocol initialization and notification sequence over HTTP.
  - Extracts and parses documents from `<untrusted-user-data>` security wrappers.
  - Provides a clean `mcp_find` interface for the agent to use.
- **Dockerization**: Complete containerization for all components:
  - `backend/Dockerfile`: Lightweight Python 3.12-slim build for Cloud Run.
  - `frontend/Dockerfile`: Multi-stage Node 22-alpine build with Next.js standalone optimization.
  - `mcp-server/Dockerfile`: Standard Node-based build for the partner tool.
- **Frontend Dashboard (Next.js & React)**: Fully scaffolded and active UI containing:
  - Sidebar and Header navigation with tab routing.
  - Interactive components: `FatigueScoreCard`, `HealthTrendChart`, `CalendarSyncStatus`, `AgentActivityFeed`, `RoutineCard`, and `MicroFeedbackModal`.
  - Configured with automatic backend polling every 10 seconds.
- **Backend Architecture (FastAPI & MongoDB)**: Fully structured backend featuring:
  - Lifespan MongoDB connection management via asynchronous **Motor** driver.
  - Structured routing: 7 routers.
  - Strict Pydantic schemas: 5 models + sub-models.
- **Mock Services / Demos**:
  - `simulator_service.py`: Generates complex biometric telemetry & user sentiment logs.
- **API Client (Frontend)**: `lib/api.ts` with typed fetch wrapper.
- **TypeScript Types**: `lib/types.ts` with matching frontend definitions.
- **README.md**: Professional documentation with architecture diagrams.

### What is Simulated (Working but needs production swap) ⚠️
- **Calendar Events** (`calendar_service.py`): Events stored in MongoDB `calendar_events` collection. Needs swap to actual Google Calendar API with OAuth2.
- **Deployment**: Components have Dockerfiles but are currently running locally. Needs deployment to Cloud Run (backend) and Vercel/Cloud Run (frontend).

### What is Missing (Pending) ❌

#### Critical — Required for Hackathon Judging
1. **Google Calendar OAuth2 + Real API** (Judging: "Beyond Chat"):
   - Need to: Set up OAuth consent screen in Google Cloud, implement OAuth router, swap `calendar_service.py`.
   - **Est: 4-5 hours**

2. **Cloud Infrastructure Deployment**:
   - Backend → Google Cloud Run.
   - Frontend → Google Cloud Run or Vercel.
   - **Est: 2-3 hours**

#### Important — For Demo Credibility
3. **Demo Video** (3 min): Not recorded — required for submission.
4. **Agent Evaluation/Observability**: Track agent performance/latency in a meta-dashboard.

#### Nice-to-Have (Tier 3)
5. Animated exercise illustrations (CSS/SVG stick figures).
6. Settings panel (currently shows "coming soon").
7. Multi-user simulation support.


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
