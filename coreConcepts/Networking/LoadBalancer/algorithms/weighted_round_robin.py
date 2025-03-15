# weighted load balancing algorithm
# Weighted Round Robin is an extension of the Round Robin algorithm that assigns requests to servers based on their weights.
# The servers with higher weights receive more requests than servers with lower weights.
# Assign a weight to each server.

# Create a list of servers, repeating each server according to its weight.
# For example:
# Server A (Weight = 3) → [A, A, A]
# Server B (Weight = 2) → [B, B]
# Server C (Weight = 1) → [C]
# Combined list: [A, A, A, B, B, C]
# Distribute requests in a cyclic manner using this list.


class WeightedRoundRobinLoadBalancer:
    def __init__(self, servers, weights):
        self.servers = servers
        self.weights = weights
        self.healthy_servers = set(servers)
        self.weighted_list = self._create_weighted_list()
        self.index = 0

    def _create_weighted_list(self):
        # create a list of servers based on their weights
        weighted_list = []
        for server, weight in zip(self.servers, self.weights):
            if server in self.healthy_servers:
                weighted_list.extend([server] * weight)
        return weighted_list

    def mark_unhealthy(self, server):
        # mark a server as unhealthy
        if server in self.healthy_servers:
            self.healthy_servers.discard(server)
            self.weighted_list = (
                self._create_weighted_list()
            )  # rebuild the weighted list

    def mark_healthy(self, server):
        # mark a server as healthy
        if server not in self.healthy_servers:
            self.healthy_servers.add(server)
            self.weighted_list = (
                self._create_weighted_list()
            )  # rebuild the weighted list

    def assign_server(self, request):
        # assigning request to the current server
        if not self.weighted_list:
            print(f"No healthy servers available for request {request}")
            return
        for _ in range(len(self.weighted_list)):
            server = self.weighted_list[self.index]
            self.index = (self.index + 1) % len(self.weighted_list)
            print(f"Request {request} assigned to {server}")
            return


# Example usage
servers = ["Server A", "Server B", "Server C"]
weights = [3, 2, 1]  # Corresponding weights
load_balancer = WeightedRoundRobinLoadBalancer(servers, weights)

# Simulate incoming requests
requests = ["Req1", "Req2", "Req3", "Req4", "Req5", "Req6", "Req7"]
for req in requests:
    load_balancer.assign_server(req)


# Mark Server B as unhealthy
print("\nMarking Server B as unhealthy...")
load_balancer.mark_unhealthy("Server B")

# Simulate more requests
requests = ["Req7", "Req8", "Req9", "Req10", "Req11", "Req12"]
for req in requests:
    load_balancer.assign_server(req)

# Mark Server B as healthy again
print("\nMarking Server B as healthy...")
load_balancer.mark_healthy("Server B")

# Simulate more requests
requests = ["Req13", "Req14", "Req15", "Req16", "Req17", "Req18"]
for req in requests:
    load_balancer.assign_server(req)
