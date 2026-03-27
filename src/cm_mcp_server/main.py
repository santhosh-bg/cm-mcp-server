import sys
import os
import logging
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("Cloudera Manager MCP Server")

@mcp.tool()
def get_service_health(service_name: str) -> str:
    """Queries Cloudera Manager for the health status of a specific service."""
    # FastMCP safely handles print() by moving it to stderr for you
    print(f"DEBUG: Checking health for {service_name}", file=sys.stderr)
    return f"Service {service_name} health: BAD (Mocked for PoC). Resource Manager is down"

def main():
    # Just run the server. FastMCP manages the pipes correctly.
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
