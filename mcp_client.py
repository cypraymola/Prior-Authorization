"""Tiny helper: call a tool on the local stdio MCP server and return its JSON result."""
import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = Path(__file__).resolve().parent / "mcp_server.py"


async def _call(name: str, args: dict) -> dict:
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER)])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(name, args)
    text = "".join(c.text for c in result.content if getattr(c, "type", "") == "text")
    if result.isError:
        raise RuntimeError(f"MCP tool '{name}' failed: {text}")
    return json.loads(text)


def call_tool(name: str, args: dict | None = None) -> dict:
    return asyncio.run(_call(name, args or {}))
