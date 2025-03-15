# algorithm to understand how round robin works in load balancer
# Round Robin is a simple algorithm that distributes the requests evenly among the servers.
# It is easy to implement and does not require any information about the servers.
# It is used when the servers are of equal specification and there are no sessions to be maintained.
# It is also used when the servers are stateless.

# Algorithm Steps
# Use a list to represent the servers.

# Use an index to keep track of the next server to assign a request.

# Cycle through the list of servers in a circular manner.
from .base import BaseLoadBalancer


class RoundRobinLoadBalancer(BaseLoadBalancer):
    def __init__(self, servers):
        super().__init__(servers)
        self.current_index = (
            0  # index to keep track of the next server to assign a request
        )

    def assign_server(self, request=None):
        # assigning request to the current server

        if not self.healthy_servers:
            self.logger.warning("No healthy servers available")
            return None

        server_list = list(self.healthy_servers)

        if not server_list:
            return None

        # Ensure index is valid for the current server list
        self.current_index = self.current_index % len(server_list)

        # Get the next server in rotation
        selected_server = server_list[self.current_index]

        # Move to the next server for the next request
        self.current_index = (self.current_index + 1) % len(server_list)

        self.logger.debug(f"Selected server: {selected_server}")
        return selected_server
