#!/usr/bin/env python3
import os
from fastmcp import FastMCP
from mochi import adopt, tick, act, follow_up, busy_today

mcp = FastMCP("Sample MCP Server")

def _user_id(context) -> str:
    """
    Derive a stable user_id. For the hack, a single-user default is fine.
    If Poke passes metadata (phone, thread id, etc.), hash it here.
    """
    raw = (context.get("user") or context.get("session") or "demo-user")
    return "u_" + str(abs(hash(str(raw))) % (10**12))

@mcp.tool(description="Greet a user by name with a welcome message from the MCP server")
def greet(name: str) -> str:
    return f"Hello, {name}! Welcome to our Mochi MCP server!"

@mcp.tool(description="Get information about the MCP server including name, version, environment, and Python version")
def get_server_info() -> dict:
    return {
        "server_name": "Mochi Pet MCP Server",
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "python_version": os.sys.version.split()[0]
    }

@mcp.tool
def mochi_adopt(context: dict = None) -> dict:
    """Adopt Mochi and say hi."""
    uid = _user_id(context or {})
    return adopt(uid)

@mcp.tool
def mochi_tick(local_hour: int, context: dict = None) -> dict:
    """Run a scheduled check-in. local_hour is 0..23 from the schedule."""
    uid = _user_id(context or {})
    return tick(uid, local_hour=local_hour)

@mcp.tool
def mochi_act(action: str, context: dict = None) -> dict:
    """Do an action: feed | play | clean | tuck."""
    uid = _user_id(context or {})
    return act(uid, action)

@mcp.tool
def mochi_follow_up(context: dict = None) -> dict:
    """A single soft follow-up. Call at most once after a missed ping."""
    uid = _user_id(context or {})
    return follow_up(uid)

@mcp.tool
def mochi_busy_today(hours: int = 24, context: dict = None) -> dict:
    """Silence Mochi for a while."""
    uid = _user_id(context or {})
    return busy_today(uid, hours)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Starting FastMCP server on {host}:{port}")
    
    mcp.run(
        transport="http",
        host=host,
        port=port,
        stateless_http=True
    )
