import time
from abc import ABC, abstractmethod
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class BaseLoadBalancer(ABC):
    """Base class for all load balancing algorithms."""

    def __init__(self, servers):
        """
        Initialize the load balancer with a list of server URLs.

        Args:
            servers (list): List of server URLs.
        """
        self.servers = servers
        self.healthy_servers = set(servers)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Metrics tracking
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0
        self.start_time = time.time()

        self.logger.info(f"Initialized with servers: {servers}")

    def mark_healthy(self, server):
        """Mark a server as healthy."""
        if server not in self.healthy_servers:
            self.healthy_servers.add(server)
            self.logger.info(f"Marked server {server} as healthy")

    def mark_unhealthy(self, server):
        """Mark a server as unhealthy."""
        if server in self.healthy_servers:
            self.healthy_servers.discard(server)
            self.logger.info(f"Marked server {server} as unhealthy")

    @abstractmethod
    def assign_server(self, request=None):
        """
        Assign a server to handle the request.

        Args:
            request: The request to be handled (optional).

        Returns:
            str: URL of the selected server.
        """
        pass

    def record_request_metrics(self, server, response_time, error=False):
        """
        Record metrics for a request.

        Args:
            server (str): The server that handled the request.
            response_time (float): The time taken to process the request.
            error (bool): Whether the request resulted in an error.
        """
        self.request_count += 1
        self.total_response_time += response_time
        if error:
            self.error_count += 1

    def get_metrics(self):
        """
        Get current load balancer metrics.

        Returns:
            dict: Dictionary containing metrics.
        """
        uptime = time.time() - self.start_time
        return {
            "uptime": uptime,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": (
                (self.error_count / self.request_count) if self.request_count > 0 else 0
            ),
            "avg_response_time": (
                (self.total_response_time / self.request_count)
                if self.request_count > 0
                else 0
            ),
            "requests_per_second": self.request_count / uptime if uptime > 0 else 0,
            "healthy_servers": len(self.healthy_servers),
            "total_servers": len(self.servers),
        }
