# least response time algorithm in load balancer
# # server based on the least response time.
#
# # The Least Response Time algorithm assigns the request to the server with the least response time.
# # This algorithm is useful when the servers have varying processing capacities or response times.
# # By distributing the requests to the server with the least response time,
# # the algorithm aims to optimize the overall system performance and reduce latency.


import time
import random


class LeastResponseTimeLoadBalancer:
    def __init__(self, servers):
        self.servers = servers  # List of servers
        self.response_times = {server: 0 for server in servers}  # Track response times
        self.healthy_servers = set(servers)  # Track healthy servers

    def mark_unhealthy(self, server):
        """Mark a server as unhealthy."""
        if server in self.healthy_servers:
            self.healthy_servers.discard(server)
            self.response_times.pop(server, None)  # Remove from response time tracking

    def mark_healthy(self, server):
        """Mark a server as healthy."""
        if server not in self.healthy_servers:
            self.healthy_servers.add(server)
            self.response_times[server] = 0  # Reset response time for the server

    def assign_request(self, request):
        """Assign a request to the server with the least response time."""
        if not self.healthy_servers:
            print(f"No healthy servers available for request {request}")
            return

        # Find the server with the least response time
        selected_server = min(
            self.response_times, key=lambda server: self.response_times[server]
        )

        # Simulate processing the request and updating the response time
        processing_time = random.uniform(0.1, 1.0)  # Simulate variable processing time
        time.sleep(processing_time)  # Simulate processing delay
        self.response_times[selected_server] = processing_time  # Update response time

        print(
            f"Request {request} assigned to {selected_server} (Response Time: {processing_time:.2f}s)"
        )


# Example usage
servers = ["Server A", "Server B", "Server C"]
load_balancer = LeastResponseTimeLoadBalancer(servers)

# Simulate incoming requests
requests = ["Req1", "Req2", "Req3", "Req4", "Req5", "Req6"]
for req in requests:
    load_balancer.assign_request(req)

# Mark Server B as unhealthy
print("\nMarking Server B as unhealthy...")
load_balancer.mark_unhealthy("Server B")

# Simulate more requests
requests = ["Req7", "Req8", "Req9", "Req10", "Req11", "Req12"]
for req in requests:
    load_balancer.assign_request(req)

# Mark Server B as healthy again
print("\nMarking Server B as healthy...")
load_balancer.mark_healthy("Server B")

# Simulate more requests
requests = ["Req13", "Req14", "Req15", "Req16", "Req17", "Req18"]
for req in requests:
    load_balancer.assign_request(req)
