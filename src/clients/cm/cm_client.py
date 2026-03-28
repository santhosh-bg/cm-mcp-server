import os
import cm_client
from cm_client.rest import ApiException
from loguru import logger

import urllib3
# Optional: Suppress the "Unverified HTTPS request" warnings in logs
# TODO: Remove this once we have a valid certificate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CMClient:
    """
    Client for Cloudera Manager API.
    """
    def __init__(self):
        """
        Initialize the CMClient.
        """
        self.cm_host = os.environ["CM_HOST"]
        self.cm_port = os.environ.get("CM_PORT", "7183")
        self.cm_user = os.environ["CM_USER"]
        self.cm_pass = os.environ["CM_PASS"]
        self.cm_api_version = os.environ.get("CM_API_VERSION", "v45")

        cm_client.configuration.username = self.cm_user
        cm_client.configuration.password = self.cm_pass
        # TODO: Remove this once we have a valid certificate
        cm_client.configuration.verify_ssl = False
    
        logger.info(f"Initializing CMClient with API client: https://{self.cm_host}:{self.cm_port}/api/{self.cm_api_version}")
        
        self.api_client = cm_client.ApiClient(f"https://{self.cm_host}:{self.cm_port}/api/{self.cm_api_version}")

    def get_service_status(self) -> str:
        """
        Get the status of a service.

        Args:
            service_name: The name of the service to get the status of.

        Returns:
            The status of the service.
        """
        # 3. Create the Services Resource
        services_api = cm_client.ServicesResourceApi(self.api_client)
    
        try:
            # 4. Read all services for the given cluster
            response = services_api.read_services("Cluster 1", view='summary')
            lines = []
            for service in response.items:
                status = f"{service.name}: State={service.service_state}, Health={service.health_summary}"
                lines.append(status)
            return "\n".join(lines)

        except ApiException as e:
            return f"Exception when calling ServicesResource->read_services: {e}"
    