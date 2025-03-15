# least response time algorithm in load balancer
# # server based on the least response time.
#
# # The Least Response Time algorithm assigns the request to the server with the least response time.
# # This algorithm is useful when the servers have varying processing capacities or response times.
# # By distributing the requests to the server with the least response time,
# # the algorithm aims to optimize the overall system performance and reduce latency.


# src/algorithms/least_response_time.py
from .base import BaseLoadBalancer
import time
import random

class LeastResponseTimeLoadBalancer(BaseLoadBalancer):
    """Least Response Time load balancing algorithm."""
    
    def __init__(self, servers, window_size=10):
        """
        Initialize the Least Response Time load balancer.
        
        Args:
            servers (list): List of server URLs.
            window_size (int): Number of recent response times to track.
        """
        super().__init__(servers)
        self.window_size = window_size
        # Track response times for each server
        self.response_times = {server: [] for server in servers}
        # Track when we last pinged each server
        self.last_ping_time = {server: 0 for server in servers}
        # How often to ping servers (in seconds)
        self.ping_interval = 5
    
    def record_response_time(self, server, response_time):
        """
        Record response time for a server.
        
        Args:
            server (str): The server that handled the request.
            response_time (float): The time taken to process the request.
        """
        if server not in self.response_times:
            self.response_times[server] = []
            
        # Add to the beginning of the list
        self.response_times[server].insert(0, response_time)
        
        # Keep only the most recent window_size entries
        if len(self.response_times[server]) > self.window_size:
            self.response_times[server] = self.response_times[server][:self.window_size]
    
    def get_average_response_time(self, server):
        """
        Get the average response time for a server.
        
        Args:
            server (str): The server to get the average response time for.
            
        Returns:
            float: The average response time or float('inf') if no data.
        """
        times = self.response_times.get(server, [])
        if not times:
            # If we have no data, return infinity so this server isn't selected
            return float('inf')
        return sum(times) / len(times)
    
    def assign_server(self, request=None):
        """
        Assign a server based on Least Response Time algorithm.
        
        Args:
            request: The request to be handled (not used in this algorithm).
            
        Returns:
            str: URL of the selected server or None if no healthy servers.
        """
        if not self.healthy_servers:
            self.logger.warning("No healthy servers available")
            return None
        
        # Calculate average response times for healthy servers
        avg_response_times = {
            server: self.get_average_response_time(server)
            for server in self.healthy_servers
        }
        
        if not avg_response_times:
            return None
        
        # Find the minimum response time
        min_time = min(avg_response_times.values())
        
        # If min_time is infinity, it means we have no data for any server
        # In this case, choose randomly
        if min_time == float('inf'):
            selected_server = random.choice(list(self.healthy_servers))
            self.logger.debug(f"No response time data, randomly selected server: {selected_server}")
            return selected_server
        
        # Find all servers with the minimum response time
        candidates = [
            server for server, time in avg_response_times.items()
            if time == min_time
        ]
        
        # If multiple servers have the same response time, choose randomly
        selected_server = random.choice(candidates)
        
        self.logger.debug(f"Selected server: {selected_server} (avg response time: {min_time:.4f}s)")
        return selected_server
    
    def should_ping_server(self, server):
        """
        Determine if we should ping a server to update its response time.
        
        Args:
            server (str): The server to check.
            
        Returns:
            bool: True if we should ping the server, False otherwise.
        """
        current_time = time.time()
        last_ping = self.last_ping_time.get(server, 0)
        return current_time - last_ping >= self.ping_interval
    
    def ping_server(self, server):
        """
        Ping a server to measure its response time.
        This should be implemented by the proxy layer.
        
        Args:
            server (str): The server to ping.
        """
        # This is a placeholder, actual implementation will be in the proxy
        pass