# ── ErgoFlow AI — MongoDB MCP Server (Cloud Run) ──────────────────────────
# Uses Node.js 22 (minimum required by mongodb-mcp-server)
# Runs in HTTP transport mode so Google Cloud Agent Builder can reach it remotely

FROM node:22-slim

WORKDIR /app

# Copy package manifest and install the MCP server
COPY package.json ./
RUN npm install --omit=dev

# Cloud Run injects PORT env var (default 8080)
# We forward it to the MCP server via MDB_MCP_HTTP_PORT
ENV MDB_MCP_TRANSPORT=http
ENV MDB_MCP_HTTP_HOST=0.0.0.0
ENV MDB_MCP_HTTP_PORT=8080
ENV MDB_MCP_READ_ONLY=true

EXPOSE 8080

# Start the MCP server
# MDB_MCP_CONNECTION_STRING is injected at deploy time via Cloud Run env vars / Secret Manager
CMD ["npx", "mongodb-mcp-server"]
