# Project Memory & Context (ErgoFlow AI)

This file serves as the long-term memory for AI agents working on this project. **AI Agents MUST read this file before beginning work and update it after completing tasks.**

## Project Overview
- **Name:** ErgoFlow AI
- **Goal:** Autonomous Context-Aware Occupational Health Agent for software engineers.
- **Spec:** See `IDEA.md` for full requirements and schemas.

## Current State (Last Updated: 2026-05-22)

### What is Completed (Done)
- **Frontend Dashboard (Next.js & React)**: Fully scaffolded and active UI containing:
  - Sidebar and Header navigation.
  - Interactive components: `FatigueScoreCard`, `HealthTrendChart` (biometrics timeline), `CalendarSyncStatus` (upcoming breaks), `AgentActivityFeed` (reasoning logs), `RoutineCard` (exercise protocols), and `MicroFeedbackModal` (qualitative muscle assessments).
  - Configured with automatic backend polling every 10 seconds and integration APIs.
- **Backend Architecture (FastAPI & MongoDB)**: Fully structured backend featuring:
  - Lifespan MongoDB connection management via asynchronous **Motor** driver.
  - Structured routing (`/api/health`, `/api/telemetry`, `/api/feedback`, `/api/agent/routines`, `/api/agent`, `/api/calendar`, `/api/simulator`).
  - Strict Pydantic schemas mapping user profiles, telemetry series, feedback loops, and activity logs.
- **Mock Services / Demos**:
  - `simulator_service.py`: Generates complex biometric telemetry & user sentiment logs representing high-fatigue, moderate, or healthy workdays.
  - `agent_service.py`: Emulates the cognitive pipeline, calculating real-time composite fatigue scores (sitting + pain + inactivity + mental) and dispatching appropriate breaks.
- **Memory Rules**: Created `.clinerules` and `.cursorrules` to force future AI agents to check and update project memory.

### What is Missing (Pending)
- **Production Google Cloud Agent Builder & Gemini 3 Integration**:
  - The cognitive reasoning pipeline in `agent_service.py` is currently simulated. We need to swap this with actual Vertex AI / Google Cloud Agent Builder tool calling APIs that consume the MongoDB MCP tool and reason dynamically.
- **Production Google Calendar API Sync**:
  - `calendar_service.py` stores mock schedules inside MongoDB. We need to implement actual Google Calendar OAuth2 and api client interactions to add real calendar events.
- **Live Biometric Telemetry Ingest Hooks**:
  - Build active integrations/webhooks for Apple HealthKit or Android Health Connect to push real user metrics into the `/api/telemetry` endpoint rather than relying on the simulated series.
- **Production MongoDB MCP Server Deployment**:
  - Map and host the MongoDB Model Context Protocol server, enabling Agent Builder's system instructions to naturally query user telemetry and subjective pain indexes.

---
*Note to AI Agents: Append new decisions, feature completions, and architectural changes below this line.*
