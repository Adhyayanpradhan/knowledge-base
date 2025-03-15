# The Least Connections algorithm is a dynamic load balancing method that distributes incoming requests to the server with the
# fewest active connections at the time of the request. Unlike Round Robin or Weighted Round Robin, which distribute requests evenly or based on static weights,
# the Least Connections algorithm adapts to the current load on each server,
# making it more efficient for scenarios where requests have varying processing times or server capacities differ.

# Algorithm Steps
# Maintain a count of active connections for each server.
# Assign the request to the server with the least active connections.
# Update the active connection count for the selected server.
# In case of a tie (multiple servers with the same least connections), use additional criteria like server weights or Round Robin to break the tie.

from .round_robin import RoundRobinLoadBalancer
from .base import BaseLoadBalancer


class LeastConnectionsLoadBalancer(BaseLoadBalancer):
    """Least Connections load balancing algorithm with Round Robin for equal connections."""

    def __init__(self, servers):
        """
        Initialize the Least Connections load balancer.

        Args:
            servers (list): List of server URLs.
        """
        super().__init__(servers)
        # Track active connections for each server
        self.connections = {server: 0 for server in servers}
        # Create a RoundRobinLoadBalancer for use when multiple servers have equal connections
        self.round_robin = RoundRobinLoadBalancer(servers)

    # def mark_unhealthy(self, server):
    #     """Mark a server as unhealthy."""
    #     if server in self.healthy_servers:
    #         self.healthy_servers.discard(server)
    #         self.connections.pop(server, None)  # Remove from connections tracking
    #         self.round_robin_load_balancer.mark_unhealthy(
    #             server
    #         )  # Update LoadBalancer health status

    # def mark_healthy(self, server):
    #     """Mark a server as healthy."""
    #     if server not in self.healthy_servers:
    #         self.healthy_servers.add(server)
    #         self.connections[server] = 0  # Reset connection count for the server

    def assign_server(self, request):
        """Assign a request to the server with the least connections."""
        if not self.healthy_servers:
            self.logger.warning("No healthy servers available")
            return None

        # Get connections for healthy servers
        healthy_connections = {
            server: self.connections.get(server, 0) for server in self.healthy_servers
        }

        if not healthy_connections:
            return None

        # Find servers with minimum connections
        min_connections = min(healthy_connections.values())
        candidates = [
            server
            for server, connections in healthy_connections.items()
            if connections == min_connections
        ]

        selected_server = None

        # If multiple servers have the same number of connections, use round robin
        if len(candidates) > 1:
            # Update the round_robin's healthy_servers to only include our candidates
            original_healthy_servers = self.round_robin.healthy_servers
            self.round_robin.healthy_servers = set(candidates)

            # Use the round robin algorithm to select among equal candidates
            selected_server = self.round_robin.assign_server(request)

            # Restore the original healthy_servers
            self.round_robin.healthy_servers = original_healthy_servers

            self.logger.debug(
                f"Multiple servers with {min_connections} connections, using round-robin"
            )
        else:
            # Only one server with minimum connections
            selected_server = candidates[0]

        # Increment the connection counter for the selected server
        self.connections[selected_server] = self.connections.get(selected_server, 0) + 1

        self.logger.debug(
            f"Selected server: {selected_server} (connections: {self.connections[selected_server]})"
        )
        return selected_server

    def complete_request(self, server):
        """Decrement the connection count when a request is completed."""
        if server in self.connections and self.connections[server] > 0:
            self.connections[server] -= 1
            self.logger.debug(
                f"Released connection from {server} (connections: {self.connections[server]})"
            )


# # Example usage
# servers = ["Server A", "Server B", "Server C"]
# load_balancer = LeastConnectionsLoadBalancer(servers)

# # Simulate incoming requests
# requests = ["Req1", "Req2", "Req3", "Req4", "Req5", "Req6"]
# for req in requests:
#     load_balancer.assign_server(req)

# # Simulate request completion
# load_balancer.complete_request("Server A")
# load_balancer.complete_request("Server B")

# # Mark Server C as unhealthy
# print("\nMarking Server C as unhealthy...")
# load_balancer.mark_unhealthy("Server C")

# # Simulate more requests
# requests = ["Req7", "Req8", "Req9", "Req10", "Req11", "Req12"]
# for req in requests:
#     load_balancer.assign_server(req)

# # Mark Server C as healthy again
# print("\nMarking Server C as healthy...")
# load_balancer.mark_healthy("Server C")

# # Simulate more requests
# requests = ["Req13", "Req14", "Req15", "Req16", "Req17", "Req18"]
# for req in requests:
#     load_balancer.assign_server(req)
