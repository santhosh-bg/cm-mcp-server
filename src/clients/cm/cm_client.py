import os
import cm_client
from cm_client.rest import ApiException
from loguru import logger
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CMClient:
    """
    Client for Cloudera Manager API.
    """
    def __init__(self, cm_host: str, cm_username: str, cm_password: str, cm_port: int = 7183):
        self.cm_host = cm_host
        self.cm_port = cm_port
        self.cm_username = cm_username
        self.cm_password = cm_password
        self.cm_api_version = os.environ.get("CM_API_VERSION", "v45")

        # Global Config
        cm_client.configuration.username = self.cm_username
        cm_client.configuration.password = self.cm_password
        cm_client.configuration.verify_ssl = False
    
        base_url = f"https://{self.cm_host}:{self.cm_port}/api/{self.cm_api_version}"
        logger.info(f"Initializing CMClient at: {base_url}")
        
        self.api_client = cm_client.ApiClient(base_url)
        
        # Pre-initialize APIs for better performance
        self.services_api = cm_client.ServicesResourceApi(self.api_client)
        self.events_api = cm_client.EventsResourceApi(self.api_client)
        self.ts_api = cm_client.TimeSeriesResourceApi(self.api_client)

    def get_service_status(self) -> str:
        """Returns the status and health of all services in the cluster."""
        try:
            response = self.services_api.read_services("Cluster 1", view='summary')
            lines = []
            for service in response.items:
                lines.append(f"{service.name}: State={service.service_state}, Health={service.health_summary}")
            
            # Return AFTER the loop finishes
            return "\n".join(lines) if lines else "No services found."

        except ApiException as e:
            return f"CM API Exception: {e}"

    def get_service_events(self, service_name: str, from_time: str, to_time: str = None) -> str:
        """Queries events for a specific service window."""
        query = (f"attributes.service=={service_name};"
                 f"timeReceived=gt={from_time};"
                 f"timeReceived=lt={to_time};"
                 f"severity==IMPORTANT,CRITICAL")
    
        try:
            response = self.events_api.read_events(query=query)
            if not response or not response.items:
                return f"No events found for {service_name}."
            
            items = response.items[:15] # Limit to 15 for AI context
            lines = [f"Found {len(response.items)} events (showing top {len(items)}):"]
            for e in items:
                # Use .time_occurred to match standard CM event schema
                lines.append(f"[{getattr(e, 'time_occurred', 'N/A')}] {e.severity}: {e.content}")
            return "\n".join(lines)
        except Exception as e:
            return f"Event query failed: {e}"

    def get_service_metrics(self, ts_query: str, from_time: str, to_time: str) -> str:
        """Executes a tsquery and returns the latest data points."""
        try:
            response = self.ts_api.query_time_series(
                query=ts_query, 
                from_time=from_time, 
                to_time=to_time
            )
            
            lines = []
            for item in response.items:
                for ts in item.time_series:
                    metric_name = ts.metadata.metric_name
                    # Extract the most recent value
                    latest_val = ts.data[-1].value if ts.data else "N/A"
                    lines.append(f"{metric_name}: {latest_val}")
            
            return "\n".join(lines) if lines else "No metric data found."
        except Exception as e:
            return f"Metrics query failed: {e}"

    def list_cluster_services(self) -> str:
        """Lists display names and internal IDs for all services."""
        try:
            response = self.services_api.read_services(cluster_name="Cluster 1", view='summary')
            lines = ["Available Services:"]
            for s in response.items:
                lines.append(f"- {s.display_name} ({s.type}) -> ID: {s.name}")
            return "\n".join(lines)
        except Exception as e:
            return f"Service list failed: {e}"