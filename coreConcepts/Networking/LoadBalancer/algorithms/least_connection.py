# The Least Connections algorithm is a dynamic load balancing method that distributes incoming requests to the server with the
# fewest active connections at the time of the request. Unlike Round Robin or Weighted Round Robin, which distribute requests evenly or based on static weights,
# the Least Connections algorithm adapts to the current load on each server,
# making it more efficient for scenarios where requests have varying processing times or server capacities differ.

# Algorithm Steps
# Maintain a count of active connections for each server.
# Assign the request to the server with the least active connections.
# Update the active connection count for the selected server.
# In case of a tie (multiple servers with the same least connections), use additional criteria like server weights or Round Robin to break the tie.

from round_robin import LoadBalancer


class LeastConnectionsLoadBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.connections = {server: 0 for server in servers}  # Track active connections
        self.healthy_servers = set(servers)  # Track healthy servers
        self.round_robin_load_balancer = LoadBalancer(servers)  # Round Robin fallback

    def mark_unhealthy(self, server):
        """Mark a server as unhealthy."""
        if server in self.healthy_servers:
            self.healthy_servers.discard(server)
            self.connections.pop(server, None)  # Remove from connections tracking
            self.round_robin_load_balancer.mark_unhealthy(
                server
            )  # Update LoadBalancer health status

    def mark_healthy(self, server):
        """Mark a server as healthy."""
        if server not in self.healthy_servers:
            self.healthy_servers.add(server)
            self.connections[server] = 0  # Reset connection count for the server

    def assign_server(self, request):
        """Assign a request to the server with the least connections."""
        if not self.healthy_servers:
            print(f"No healthy servers available for request {request}")
            return None

        # Find the minimum number of active connections among healthy servers
        least_connections = min(
            self.connections[server] for server in self.healthy_servers
        )

        # Find all servers with the minimum number of connections
        least_connection_servers = [
            server
            for server in self.healthy_servers
            if self.connections[server] == least_connections
        ]

        # print(f"Least connections: {least_connections}")
        # print(f"Least connection servers: {least_connection_servers}")

        # If there are multiple servers with the same number of connections,
        # use the LoadBalancer class to select one using round-robin
        if len(least_connection_servers) > 1:
            selected_server = self.round_robin_load_balancer.assign_server(
                least_connection_servers
            )
        else:
            selected_server = least_connection_servers[0]

        # Update the connection count for the selected server
        self.connections[selected_server] += 1
        print(
            f"Request {request} assigned to {selected_server} (Connections: {self.connections[selected_server]})"
        )

        return selected_server

    def complete_request(self, server):
        """Decrement the connection count when a request is completed."""
        if server in self.connections and self.connections[server] > 0:
            self.connections[server] -= 1
            print(
                f"Request completed on {server} (Connections: {self.connections[server]})"
            )


# Example usage
servers = ["Server A", "Server B", "Server C"]
load_balancer = LeastConnectionsLoadBalancer(servers)

# Simulate incoming requests
requests = ["Req1", "Req2", "Req3", "Req4", "Req5", "Req6"]
for req in requests:
    load_balancer.assign_server(req)

# Simulate request completion
load_balancer.complete_request("Server A")
load_balancer.complete_request("Server B")

# Mark Server C as unhealthy
print("\nMarking Server C as unhealthy...")
load_balancer.mark_unhealthy("Server C")

# Simulate more requests
requests = ["Req7", "Req8", "Req9", "Req10", "Req11", "Req12"]
for req in requests:
    load_balancer.assign_server(req)

# Mark Server C as healthy again
print("\nMarking Server C as healthy...")
load_balancer.mark_healthy("Server C")

# Simulate more requests
requests = ["Req13", "Req14", "Req15", "Req16", "Req17", "Req18"]
for req in requests:
    load_balancer.assign_server(req)
