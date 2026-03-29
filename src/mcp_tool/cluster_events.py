from datetime import datetime, timezone, timedelta
from loguru import logger
from mcp.types import CallToolResult, TextContent
from pydantic import Field
from typing import Optional

class ClusterServiceEvents:
    def __init__(self, mcp, cm_client_instance):
        self.mcp = mcp
        self.cm_client_instance = cm_client_instance
        self.mcp.add_tool(self.get_service_events)

    def _format_timestamp(self, ts: str) -> str:
        """Ensures timestamp is ISO-8601 with Zulu suffix."""
        if not ts: return ts
        ts = ts.replace(" ", "T")
        if not ts.endswith('Z') and '+' not in ts:
            ts += 'Z'
        return ts

    def get_service_events(
        self, 
        service_name: str, 
        from_time: Optional[str] = Field(
            default=None,
            description="Start time (ISO-8601). e.g. 2026-03-29T00:45:00Z. Defaults to 1h ago."
        ),
        to_time: Optional[str] = Field(
            default=None,
            description="End time (ISO-8601). Defaults to NOW."
        )
    ) -> CallToolResult:
        """
        Queries Cloudera Manager Events to investigate service failures (e.g., HDFS-1, KAFKA-1).
        This tool extracts the 'content' field to explain WHY a service is failing.
        """
        if not self.cm_client_instance:
            return CallToolResult(isError=True, content=[TextContent(type='text', text="CM Client uninitialized")])

        # Handle Defaults
        now = datetime.now(timezone.utc)
        f_time = self._format_timestamp(from_time) or (now - timedelta(hours=1)).isoformat().replace("+00:00", "Z")
        t_time = self._format_timestamp(to_time) or now.isoformat().replace("+00:00", "Z")

        # Build the query based on your successful CURL test
        # Note: We use 'IMPORTANT' severity as a baseline for troubleshooting
        query = (
            f"attributes.service=={service_name};"
            f"timeReceived=gt={f_time};"
            f"timeReceived=lt={t_time};"
            f"severity==IMPORTANT"
        )

        try:
            logger.info(f"Fetching events for {service_name} with query: {query}")
            
            # Using the api_client directly via the events resource
            import cm_client
            events_api = cm_client.EventsResourceApi(self.cm_client_instance.api_client)
            
            # maxResults
            response = events_api.read_events(query=query, max_results=15)

            if not response or not hasattr(response, 'items') or not response.items:
                return CallToolResult(
                    isError=False,
                    content=[TextContent(type='text', text=f"No critical events found for {service_name} in the selected window.")]
                )

            # Parse the content field into a readable summary for the AI
            event_lines = [f"Summary for {service_name} ({f_time} to {t_time}):"]
            for item in response.items:
                # Extracting core info from the JSON structure
                timestamp = getattr(item, 'time_occurred', 'Unknown Time')
                content = getattr(item, 'content', 'No description provided')
                severity = getattr(item, 'severity', 'INFO')
                
                event_lines.append(f"[{timestamp}] {severity}: {content}")

            return CallToolResult(
                isError=False,
                content=[TextContent(type='text', text="\n".join(event_lines))]
            )

        except Exception as e:
            logger.error(f"Event Tool Error: {e}")
            return CallToolResult(
                isError=True,
                content=[TextContent(type='text', text=f"Failed to fetch events: {str(e)}")]
            )