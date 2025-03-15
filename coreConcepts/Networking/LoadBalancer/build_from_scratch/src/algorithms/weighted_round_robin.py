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

from .base import BaseLoadBalancer


class WeightedRoundRobinLoadBalancer(BaseLoadBalancer):
    def __init__(self, servers, weights=None):
        super().__init__(servers)

        if weights is None:
            weights = {server: 1 for server in servers}

        self.weights = weights

        self.current_weight = 0

        self.current_index = 0
        self.max_weight = max(weights.values()) if weights else 0

        self.logger.info(f"Initialized with weights: {weights}")

    # def _create_weighted_list(self):
    #     # create a list of servers based on their weights
    #     weighted_list = []
    #     for server, weight in zip(self.servers, self.weights):
    #         if server in self.healthy_servers:
    #             weighted_list.extend([server] * weight)
    #     return weighted_list

    # def mark_unhealthy(self, server):
    #     # mark a server as unhealthy
    #     if server in self.healthy_servers:
    #         self.healthy_servers.discard(server)
    #         self.weighted_list = (
    #             self._create_weighted_list()
    #         )  # rebuild the weighted list

    # def mark_healthy(self, server):
    #     # mark a server as healthy
    #     if server not in self.healthy_servers:
    #         self.healthy_servers.add(server)
    #         self.weighted_list = (
    #             self._create_weighted_list()
    #         )  # rebuild the weighted list

    def assign_server(self, request=None):
        # assigning request to the current server
        if not self.healthy_servers:
            print(f"No healthy servers available for request {request}")
            return None

        # Filter servers to only include healthy ones
        healthy_weights = {
            server: self.weights.get(server, 1) for server in self.healthy_servers
        }

        if not healthy_weights:
            return None

        # Implementation of Smooth Weighted Round Robin
        # This ensures more even distribution over time
        server_list = list(healthy_weights.keys())

        # If only one server, return it
        if len(server_list) == 1:
            return server_list[0]

        # Get highest weight server
        selected_server = None
        highest_weight = 0

        for server, weight in healthy_weights.items():
            # We use a modifiable weight that gets updated each time
            current_effective_weight = weight

            if current_effective_weight > highest_weight:
                highest_weight = current_effective_weight
                selected_server = server

        # Update weights for next selection
        # This ensures that servers with higher weights get selected more often,
        # but in a more distributed way over time
        new_weights = {}
        for server, weight in healthy_weights.items():
            if server == selected_server:
                new_weights[server] = weight - sum(healthy_weights.values()) + weight
            else:
                new_weights[server] = weight + weight

        self.weights.update(new_weights)

        self.logger.debug(f"Selected server: {selected_server}")
        return selected_server

    def update_weight(self, server, weight):
        """
        Update the weight of a server.

        Args:
            server (str): The server to update.
            weight (int): The new weight.
        """
        self.weights[server] = weight
        self.max_weight = max(self.weights.values())
        self.logger.info(f"Updated weight for {server} to {weight}")


# # Example usage
# servers = ["Server A", "Server B", "Server C"]
# weights = [3, 2, 1]  # Corresponding weights
# load_balancer = WeightedRoundRobinLoadBalancer(servers, weights)

# # Simulate incoming requests
# requests = ["Req1", "Req2", "Req3", "Req4", "Req5", "Req6", "Req7"]
# for req in requests:
#     load_balancer.assign_server(req)


# # Mark Server B as unhealthy
# print("\nMarking Server B as unhealthy...")
# load_balancer.mark_unhealthy("Server B")

# # Simulate more requests
# requests = ["Req7", "Req8", "Req9", "Req10", "Req11", "Req12"]
# for req in requests:
#     load_balancer.assign_server(req)

# # Mark Server B as healthy again
# print("\nMarking Server B as healthy...")
# load_balancer.mark_healthy("Server B")

# # Simulate more requests
# requests = ["Req13", "Req14", "Req15", "Req16", "Req17", "Req18"]
# for req in requests:
#     load_balancer.assign_server(req)

## test
# Example usage
servers = ["Server A", "Server B", "Server C"]
weights = {"Server A": 3, "Server B": 2, "Server C": 1}
load_balancer = WeightedRoundRobinLoadBalancer(servers, weights)

# Simulate incoming requests
requests = ["Req1", "Req2", "Req3", "Req4", "Req5", "Req6", "Req7"]
for req in requests:
    selected_server = load_balancer.assign_server(req)
    print(f"Request {req} assigned to {selected_server}")

# Mark Server B as unhealthy
print("\nMarking Server B as unhealthy...")
load_balancer.mark_unhealthy("Server B")

# Simulate more requests
requests = ["Req8", "Req9", "Req10", "Req11", "Req12"]
for req in requests:
    selected_server = load_balancer.assign_server(req)
    print(f"Request {req} assigned to {selected_server}")

# Mark Server B as healthy again
print("\nMarking Server B as healthy...")
load_balancer.mark_healthy("Server B")

# Simulate more requests
requests = ["Req13", "Req14", "Req15", "Req16", "Req17", "Req18"]
for req in requests:
    selected_server = load_balancer.assign_server(req)
    print(f"Request {req} assigned to {selected_server}")
