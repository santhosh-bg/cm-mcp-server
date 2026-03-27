import sys
import os
from mcp.server.fastmcp import FastMCP

# Redirect ALL stdout to stderr immediately to protect the MCP pipe
sys.stdout = sys.stderr

# Initialize FastMCP Server
mcp = FastMCP("Cloudera Manager MCP Server")

@mcp.tool()
def get_service_health(service_name: str) -> str:
    """Queries Cloudera Manager for the health status of a specific service."""
    # Ensure this returns a string, not an object
    return f"Service {service_name} health: BAD (Mocked for PoC). Resource Manager is down"

def main():
    # print("Hello from cm-mcp-server!")
    mcp.run()

if __name__ == "__main__":
    main()
