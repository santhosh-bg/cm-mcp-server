import sys
import os
from loguru import logger
from mcp.server.fastmcp import FastMCP
from clients.cm.cm_client import CMClient

# Define server instructions and dependencies
SERVER_INSTRUCTIONS = """
# Cloudera Manaager MCP Server

This MCP server provides tools for read-only operations on Cloudera Manager managed CDP Cluster.

## IMPORTANT: Use MCP Tools for Cloudera Manager Cluster Read-Only Operations

DO NOT use MCP for Cloudera Manager Cluster write operations.

## Usage Notes

- By default, the server runs in read-only mode. 
- Use the `get_cdp_cluster_health` tool to find the service health for CDP service components like YARN, Spark, Kudu etc.

"""

cm = CMClient()

# Initialize FastMCP Server. Doing it first since we will be using stdio as transport.
mcp = FastMCP("Cloudera Manager MCP Server", instructions=SERVER_INSTRUCTIONS)

@mcp.tool()
def get_cdp_cluster_health() -> str:
    """
    Returns the health of each CDP services in Cloudera Manager managed cluster.
    """

    return cm.get_service_status()


def main():
    logger.info("Starting the MCP Server")
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
