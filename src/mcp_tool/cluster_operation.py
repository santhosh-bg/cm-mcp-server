from loguru import logger
from mcp.types import CallToolResult, TextContent

class ClusterOperation:

    def __init__(self, mcp, cm_client_instance):
        self.mcp = mcp
        self.cm_client_instance = cm_client_instance
        self.mcp.add_tool(self.get_service_health)
        self.mcp.add_tool(self.list_cluster_services)
    

    def get_service_health(self) -> CallToolResult:
        """
        Returns the health of each CDP service in the Cloudera Manager managed cluster.
        """
        if not self.cm_client_instance:
            return "Error: CM Client is not initialized. Check server logs for configuration errors."
    
        try:
            data = self.cm_client_instance.get_service_status()
            return CallToolResult(
                isError=False,
                content=[TextContent(type='text', text=data)],
            )
        except Exception as e:
            # This tells the AI the tool failed, rather than just returning error text
            return CallToolResult(
                isError=True,
                content=[TextContent(type='text', text=f"CM API Error: {str(e)}")],
            )

    
    def list_cluster_services(self) -> CallToolResult:
        """
        Lists all services in the cluster with their display names and internal IDs.
        Use this to find the correct 'service_name' (e.g., 'HDFS-1') before calling 
        event or metric tools.
        """
        
        if not self.cm_client_instance:
            return "Error: CM Client is not initialized. Check server logs for configuration errors."
        try:
            response = self.cm_client_instance.list_cluster_services()
            return CallToolResult(
                isError=False,
                content=[TextContent(type='text', text=response)],
            )
        except Exception as e:
            # This tells the AI the tool failed, rather than just returning error text
            return CallToolResult(
                isError=True,
                content=[TextContent(type='text', text=f"CM API Error: {str(e)}")],
            )
            