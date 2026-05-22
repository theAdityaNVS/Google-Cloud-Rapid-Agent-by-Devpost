# ErgoFlow AI — MongoDB MCP Server

This directory contains the configuration for the MongoDB MCP Server that exposes the ErgoFlow Atlas database to **Google Cloud Agent Builder** (Gemini 3) via the Model Context Protocol.

---

## What This Does

The `mongodb-mcp-server` (official package by MongoDB) runs as a standalone HTTP service. When registered in Agent Builder as an MCP Tool, Gemini 3 can call it to:
- Query `biometric_telemetry` for the user's latest metrics
- Read `subjective_feedback` to understand pain levels
- Read `orchestrated_routines` to check scheduled sessions
- Read `agent_activity_log` for observability

The server is **read-only** — all write operations (inserting telemetry, creating routines) go through the FastAPI backend.

---

## Phase 1 — Local Test (no GCP needed)

```powershell
# Set env vars and run the server locally
$env:MDB_MCP_CONNECTION_STRING="mongodb+srv://admin:admin@ergoai.ofo6lhr.mongodb.net/?appName=ErgoAI"
$env:MDB_MCP_TRANSPORT="http"
$env:MDB_MCP_HTTP_HOST="0.0.0.0"
$env:MDB_MCP_HTTP_PORT="8080"
$env:MDB_MCP_READ_ONLY="true"
npx -y mongodb-mcp-server@latest
```

Server starts at: `http://localhost:8080`

---

## Phase 2 — Deploy to Google Cloud Run

### Prerequisites
1. `gcloud` CLI installed and authenticated
2. Google Cloud project created with billing enabled
3. APIs enabled: Cloud Run, Cloud Build, Artifact Registry

### Step 1: Create Project (if not done)
```bash
gcloud projects create ergoflow-ai-hackathon --name="ErgoFlow AI"
gcloud config set project ergoflow-ai-hackathon
gcloud billing projects link ergoflow-ai-hackathon --billing-account=YOUR_BILLING_ACCOUNT_ID
```

### Step 2: Enable APIs
```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

### Step 3: Deploy to Cloud Run (from this directory)
```bash
gcloud run deploy ergoflow-mongodb-mcp \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars "MDB_MCP_TRANSPORT=http,MDB_MCP_HTTP_HOST=0.0.0.0,MDB_MCP_HTTP_PORT=8080,MDB_MCP_READ_ONLY=true" \
  --set-env-vars "MDB_MCP_CONNECTION_STRING=mongodb+srv://admin:admin@ergoai.ofo6lhr.mongodb.net/?appName=ErgoAI"
```

> **Note**: `--allow-unauthenticated` is used here for hackathon demo simplicity. For production, use `--no-allow-unauthenticated` and configure IAM.

### Step 4: Get the URL
```bash
gcloud run services describe ergoflow-mongodb-mcp --region us-central1 --format 'value(status.url)'
```

Save this URL — you'll need it when registering the MCP tool in Agent Builder.

---

## Registering in Google Cloud Agent Builder

1. Open [Agent Builder / Agent Studio](https://console.cloud.google.com/gen-app-builder/agents)
2. Select your agent → **Tools** tab → **+ Add Tool**
3. Select **MCP Tool**
4. Fill in:
   - **Name**: `mongodb-ergoflow`
   - **Description**: `Query ErgoFlow AI health database — biometric telemetry, subjective feedback, routines`
   - **Server URL**: `https://ergoflow-mongodb-mcp-XXXX-uc.a.run.app`
5. Save and test with a query like: *"What is the latest biometric telemetry for user usr_dev_9981?"*

---

## Collections Available to Agent

| Collection | Data | Agent Use |
|---|---|---|
| `biometric_telemetry` | Steps, HRV, sitting time, stand hours | Detect inactivity / fatigue patterns |
| `subjective_feedback` | Pain scores (back, shoulder, neck, eyes) | Determine intervention urgency |
| `orchestrated_routines` | Scheduled exercise protocols | Check if routine already exists |
| `agent_activity_log` | Agent reasoning history | Observability and tracing |
