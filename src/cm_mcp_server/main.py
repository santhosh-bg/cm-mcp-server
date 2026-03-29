import sys
import os
import argparse
from loguru import logger
from mcp.server.fastmcp import FastMCP
from clients.cm.cm_client import CMClient
from mcp_tool.cluster_service_operation import ClusterServiceOperation
from mcp_tool.cluster_events import ClusterServiceEvents

# Define server instructions and dependencies
SERVER_INSTRUCTIONS = """
# Cloudera Manaager MCP Server

This MCP server provides tools for read-only operations on Cloudera Manager managed CDP Cluster.

## IMPORTANT: Use MCP Tools for Cloudera Manager Cluster Read-Only Operations

DO NOT use MCP for Cloudera Manager Cluster write operations.

## GUIDELINES

- By default, the server runs in read-only mode. 
- Use the `get_cdp_cluster_health` tool to find the service health for CDP service components like YARN, Spark, Kudu etc.

## SERVICE NAMING CONVENTIONS
- Cloudera Manager uses internal IDs like 'HDFS-1' or 'KAFKA-1'.
- If the user mentions 'HDFS', always check if 'HDFS-1' is the correct ID.
- If unsure of a service ID, ALWAYS call 'list_cluster_services' first. 
- DO NOT guess service IDs if 'list_cluster_services' has not been called in this session.

"""

# 1. Initialize FastMCP at the top level
mcp = FastMCP("Cloudera Manager MCP Server")

# 2. Define a global placeholder for your client
cm_client_instance = None

def main():
    global cm_client_instance
    
    parser = argparse.ArgumentParser(description="Cloudera Manager MCP Server")
    parser.add_argument("--host", help="CM Host (Env: CM_HOST)")
    parser.add_argument("--port", help="CM Port (Env: CM_PORT, Default: 7183)", default="7183")
    parser.add_argument("--user", help="CM Username (Env: CM_USER)")
    parser.add_argument("--password", help="CM Password (Env: CM_PASS)")
    args = parser.parse_args()

    # Priority: Env Var > CLI Arg
    cm_host = os.getenv("CM_HOST") or args.host
    cm_user = os.getenv("CM_USER") or args.user
    cm_pass = os.getenv("CM_PASS") or args.password
    cm_port = os.getenv("CM_PORT") or args.port

    # Validation
    if not all([cm_host, cm_user, cm_pass]):
        logger.error("Missing required configuration (Host, User, or Password).")
        sys.exit(1)

    try:
        # 4. Initialize the global client instance
        cm_client_instance = CMClient(
            cm_host=cm_host,
            cm_username=cm_user,
            cm_password=cm_pass,
            cm_port=int(cm_port),
        )
        
        logger.info(f"Starting MCP Server for CM Host: {cm_host}")
        # init mcp tool
        init_mcp_tool(mcp, cm_client_instance)
        
        mcp.run(transport="stdio")
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
    
def init_mcp_tool(mcp, cm_client_instance):
    """
    Init the mcp tooling
    """
    ClusterServiceOperation(mcp, cm_client_instance)
    ClusterServiceEvents(mcp, cm_client_instance)


if __name__ == "__main__":
    main()
    