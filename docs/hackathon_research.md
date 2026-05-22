# Google Cloud Rapid Agent Hackathon — Research Notes

## 1. Hackathon Overview

| Field | Detail |
|---|---|
| **Name** | Google Cloud Rapid Agent Hackathon |
| **Platform** | [Devpost](https://rapid-agent.devpost.com/) |
| **Dates** | May 1, 2026 → June 11, 2026 (2:00 PM PDT) |
| **Total Prize Pool** | $50,000 |
| **Eligibility** | Individuals, student teams, early-stage startups worldwide |

---

## 2. Partner Bucket System (Tracks)

Each partner track has its own prize pool. You choose ONE partner to compete under.

| Partner | Prize Pool | 1st | 2nd | 3rd |
|---|---|---|---|---|
| **Arize** | $10,000 | $5,000 | $3,000 | $2,000 |
| **Elastic** | $10,000 | $5,000 | $3,000 | $2,000 |
| **Fivetran** | $10,000 | $5,000 | $3,000 | $2,000 |
| **GitLab** | $10,000 | $5,000 | $3,000 | $2,000 |
| **MongoDB** | $10,000 | $5,000 | $3,000 | $2,000 |
| *(Dynatrace may also be listed)* | — | — | — | — |

---

## 3. Judging Criteria (3 Core Requirements)

### 3.1 Beyond Chat
The agent must **perform an actual task** — manage a database, automate a workflow, call an API — not just generate text responses.

### 3.2 Multi-Step Planning
The system must demonstrate the ability to take a complex goal, **break it down into logical steps**, and execute them under user oversight.

### 3.3 Partner Power (MCP Integration)
Must integrate at **least one** participating partner's MCP server as the bridge between the agent and the partner's data/tools.

### General Evaluation Axes
- Innovation
- Technical implementation
- Potential impact
- Overall completeness

---

## 4. Required Tech Stack

| Component | Requirement |
|---|---|
| **LLM / Brain** | Gemini 3 |
| **Orchestration** | Google Cloud Agent Builder (now Gemini Enterprise Agent Platform) |
| **External Tools** | Model Context Protocol (MCP) — must use at least 1 partner MCP server |

---

## 5. MongoDB MCP Server Setup

- **Package**: `mongodb-mcp-server` (npm)
- **Runtime**: Node.js 18+
- **Quick Start**: `npx -y mongodb-mcp-server --connectionString "YOUR_CONNECTION_STRING"`
- **Security**: Use read-only DB user for queries; elevated permissions only for admin tasks
- **Integration with Agent Builder**: Register as MCP Tool in Agent Studio → provide server address, description, authentication

---

## 6. Google Cloud Agent Builder / Agent Platform

### Two Paths
1. **Agent Studio** (low-code, visual) — good for prototyping
2. **Agent Development Kit (ADK)** (code-first, Python/Go/Java/TS) — good for complex logic

### MCP Tool Registration in Agent Studio
1. Open Agent Studio → Tool icon
2. Select "MCP Tool"
3. Provide: server name, description, server address (e.g., Cloud Run URL)
4. Configure auth (Service Agent ID Token for Cloud Run)

### Managed MCP Servers Available
Google provides managed servers for BigQuery, Maps, GKE, Compute Engine — no custom code needed.

---

## 7. Winning Strategy Insights

### What Judges Want
- **Functional, real-world agentic workflows** (not just chatbots)
- **Evidence of multi-step reasoning and tool use**
- **Clear problem → solution narrative**
- **Production-readiness**: hosted deployment, clean codebase, partner integration
- **Strong demo video** (under 3 minutes, polished)
- **Intuitive UI/UX** — judges need to immediately see value

### Anti-Patterns to Avoid
- Over-engineering beyond what can be demoed
- Generic / vague problem statements
- Text-only agents (no real actions)
- Last-minute demo videos
- Missing partner MCP integration

### Differentiators
- Evaluation & observability of agent performance
- Multi-agent collaboration workflows
- Multimodal capabilities (images, etc.)
- Clear documentation and README

---

## 8. ErgoFlow AI — Current Idea Summary

**Track**: MongoDB
**Concept**: Autonomous occupational health agent for software engineers

### Core Loop
1. Ingest biometric telemetry (HealthKit/Google Fit) + calendar state
2. Collect subjective micro-feedback (1-click pain/fatigue scores)
3. Gemini 3 reasons over data via MongoDB MCP
4. Agent autonomously schedules recovery routines into Google Calendar
5. Generates tailored mobility protocols stored in MongoDB

### Proposed Stack
- Frontend: React/Vue SPA dashboard
- Backend: Java/Spring Boot
- Database: MongoDB Atlas (via MCP)
- AI: Google Cloud Agent Builder + Gemini 3

### Data Collections
- `user_profiles` — preferences, targets
- `biometric_telemetry` — time-series health data
- `subjective_feedback` — qualitative micro-prompt scores
- `orchestrated_routines` — AI-generated recovery protocols
