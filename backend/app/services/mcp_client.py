"""
ErgoFlow AI — MongoDB MCP HTTP Client
Makes JSON-RPC calls to the deployed mongodb-mcp-server on Cloud Run.
Uses the MCP Streamable HTTP protocol (initialize → notifications/initialized → tools/call).
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger("ergoflow")

_MCP_BASE = (
    settings.mcp_server_url
    or "https://ergoflow-mongodb-mcp-555089344520.us-central1.run.app"
)
_DB_NAME = settings.mongodb_db_name or "ergoflow_db"

# Regex to extract JSON from the untrusted-user-data wrapper the MCP server adds
_UNTRUSTED_RE = re.compile(
    r"<untrusted-user-data-[^>]+>(.*?)</untrusted-user-data-[^>]+>",
    re.DOTALL,
)


def _parse_sse_data(text: str) -> dict:
    """Extract the first JSON object from an SSE response."""
    for line in text.splitlines():
        if line.startswith("data:"):
            return json.loads(line[5:].strip())
    return {}


def _extract_documents(raw: dict) -> list:
    """
    Pull document list from an MCP tools/call response.
    The server puts a summary in content[0] and the JSON in content[1],
    wrapped in <untrusted-user-data-...> security tags.
    The tag UUID also appears verbatim in the warning preamble, so we use
    findall and take the LAST match (which is the actual data block).
    """
    content = raw.get("result", {}).get("content", [])
    for item in content:
        if item.get("type") != "text":
            continue
        text = item.get("text", "")
        for match in _UNTRUSTED_RE.findall(text):
            try:
                data = json.loads(match.strip())
                if isinstance(data, list):
                    return data
            except (json.JSONDecodeError, ValueError):
                pass
    return []


async def mcp_find(
    collection: str,
    filter_: dict,
    sort: dict | None = None,
    limit: int = 5,
) -> list:
    """Query a MongoDB collection via the deployed MCP server."""
    hdrs = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    args: dict[str, Any] = {
        "database": _DB_NAME,
        "collection": collection,
        "filter": filter_,
        "limit": limit,
    }
    if sort:
        args["sort"] = sort

    async with httpx.AsyncClient(timeout=20.0) as client:
        # 1. Initialize session
        init_resp = await client.post(
            f"{_MCP_BASE}/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "ergoflow-backend", "version": "1.0"},
                },
            },
            headers=hdrs,
        )
        init_resp.raise_for_status()
        session_id = init_resp.headers.get("mcp-session-id", "")
        session_hdrs = {**hdrs, "mcp-session-id": session_id}

        # 2. Send initialized notification (required by protocol)
        await client.post(
            f"{_MCP_BASE}/mcp",
            json={"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
            headers=session_hdrs,
        )

        # 3. Make the tool call
        tool_resp = await client.post(
            f"{_MCP_BASE}/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "find", "arguments": args},
            },
            headers=session_hdrs,
        )
        tool_resp.raise_for_status()

    raw = _parse_sse_data(tool_resp.text)
    docs = _extract_documents(raw)
    logger.info("mcp_find %s → %d doc(s)", collection, len(docs))
    return docs
