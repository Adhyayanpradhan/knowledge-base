# algorithm to understand how round robin works in load balancer
# Round Robin is a simple algorithm that distributes the requests evenly among the servers.
# It is easy to implement and does not require any information about the servers.
# It is used when the servers are of equal specification and there are no sessions to be maintained.
# It is also used when the servers are stateless.

# Algorithm Steps
# Use a list to represent the servers.

# Use an index to keep track of the next server to assign a request.

# Cycle through the list of servers in a circular manner.


class LoadBalancer:
    def __init__(self, servers):
        self.servers = servers  # list of servers
        self.index = 0  # index to keep track of the next server to assign a request
        self.healthy_servers = set(servers)  # set of healthy servers

    def mark_unhealthy(self, server):
        self.healthy_servers.discard(server)

    def assign_server(self, servers=None):
        # assigning request to the current server

        if servers is None:
            servers = list(self.healthy_servers)

        for _ in range(len(self.servers)):
            server = self.servers[self.index]

            # move to next server
            self.index = (self.index + 1) % len(self.servers)

            if server in self.healthy_servers:

                return server
        return None


# servers = ["Server A", "Server B", "Server C"]  # List of servers
# load_balancer = LoadBalancer(servers)

# # load_balancer.mark_unhealthy("Server B")  # Marking Server B as unhealthy

# # Simulate incoming requests
# requests = ["Req1", "Req2", "Req3", "Req4", "Req5", "Req6"]
# for req in requests:
#     load_balancer.assign_server(req)
