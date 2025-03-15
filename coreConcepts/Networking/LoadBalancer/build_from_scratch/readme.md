The codebase implements a load balancer designed to distribute incoming HTTP requests across multiple backend servers. The primary goal of this load balancer is to efficiently manage traffic, ensuring that requests are handled by the most appropriate server based on the selected load balancing algorithm. This helps optimize resource utilization, improve response times, and enhance the overall reliability and performance of the system.
The codebase implements a load balancer designed to distribute incoming HTTP requests across multiple backend servers. The primary goal of this load balancer is to efficiently manage traffic, ensuring that requests are handled by the most appropriate server based on the selected load balancing algorithm. This helps optimize resource utilization, improve response times, and enhance the overall reliability and performance of the system.

### Key Features and Goals:

1. **Load Balancing Algorithms**:

   - The system supports multiple load balancing strategies, including:
     - **Round Robin**: Distributes requests evenly across all servers.
     - **Weighted Round Robin**: Distributes requests based on server weights, allowing some servers to handle more requests than others.
     - **Least Connections**: Directs requests to the server with the fewest active connections, which is useful for handling varying loads.
     - **Least Response Time**: Chooses the server with the shortest response time, optimizing for speed and efficiency.

2. **Dynamic Server Management**:

   - The load balancer can mark servers as healthy or unhealthy based on their status, ensuring that only available servers receive requests.
   - Health checks are performed periodically to update the status of each server.

3. **Metrics and Logging**:

   - The system tracks various metrics, such as request count, error rate, and response times, to monitor performance and identify potential issues.
   - Logging is used extensively to provide insights into the load balancer's operations and decisions.

4. **Scalability and Flexibility**:

   - The load balancer is designed to be flexible, allowing for easy configuration of different algorithms and server lists through environment variables.
   - It is containerized using Docker, making it easy to deploy and scale in different environments.

5. **Proxy Functionality**:
   - The `LoadBalancerProxy` class acts as an HTTP proxy, forwarding requests to backend servers based on the load balancer's decisions.
   - It handles various HTTP methods and manages request forwarding, response handling, and error management.

### Code References:

- **Algorithm Selection**: The algorithm is chosen based on the `ALGORITHM` environment variable, as seen in `src/main.py`.

```52:68:src/main.py
def main():
    # Get configuration from environment
    algorithm = os.environ.get("ALGORITHM", "round_robin")
    backend_servers_str = os.environ.get(
        "BACKEND_SERVERS", "http://localhost:5001,http://localhost:5002"
    )
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8080))
    # Create the load balancer
    # Parse backend servers
    backend_servers = backend_servers_str.split(",")
    # Create and run the proxy
    logger.info(f"Starting load balancer with algorithm: {algorithm}")
    logger.info(f"Backend servers: {backend_servers}")

    # Create the load balancer
    load_balancer = create_load_balancer(algorithm, backend_servers)
```

- **Load Balancer Implementation**: Each algorithm is implemented in its respective module, such as `LeastConnectionsLoadBalancer` in `src/algorithms/least_connection.py`.

```16:96:src/algorithms/least_connection.py
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
```

- **Proxy Setup**: The `LoadBalancerProxy` class in `src/proxy/http_proxy.py` sets up the FastAPI routes and manages request forwarding.

```14:162:src/proxy/http_proxy.py
class LoadBalancerProxy:
    """HTTP Proxy that uses a load balancer to route requests."""

    def __init__(self, load_balancer, host="0.0.0.0", port=8080):
        """
        Initialize the HTTP proxy.

        Args:
            load_balancer: The load balancer to use.
            host (str): Host to bind the proxy to.
            port (int): Port to bind the proxy to.
        """
        self.load_balancer = load_balancer
        self.host = host
        self.port = port
        self.app = FastAPI()
        self.logger = logging.getLogger("LoadBalancerProxy")
        self.setup_routes()

        # Start health check thread
        self.health_check_thread = threading.Thread(
            target=self.health_check_loop, daemon=True
        )
        self.health_check_thread.start()

    def setup_routes(self):
        """Set up the FastAPI routes."""

        @self.app.api_route(
            "/{path:path}",
            methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
        )
        async def proxy(path: str, request: Request):
            start_time = time.time()

            # Get a server from the load balancer
            server = self.load_balancer.assign_server(request)

            if not server:
                self.logger.error("No servers available")
                return JSONResponse(
                    content={"error": "No servers available"}, status_code=503
                )

            # Forward the request to the selected server
            try:
                url = f"{server}/{path}"
                self.logger.info(f"Forwarding request to {url}")

                # Create the proxied request
                resp = requests.request(
                    method=request.method,
                    url=url,
                    headers={
                        key: value
                        for (key, value) in request.headers.items()
                        if key != "host"
                    },
                    data=await request.body(),
                    cookies=request.cookies,
                    allow_redirects=False,
                    timeout=10,
                )

                # Calculate response time
                response_time = time.time() - start_time

                # Update load balancer metrics
                if hasattr(self.load_balancer, "record_response_time"):
                    self.load_balancer.record_response_time(server, response_time)

                self.load_balancer.record_request_metrics(
                    server, response_time, error=resp.status_code >= 500
                )

                # If using least connections, release the connection
                if hasattr(self.load_balancer, "release_connection"):
                    self.load_balancer.release_connection(server)

                # Log the request
                self.logger.info(
                    f"Request completed: {resp.status_code} in {response_time:.4f}s"
                )

                # Return the response to the client
                response = Response(content=resp.content, status_code=resp.status_code)
                for k, v in resp.headers.items():
                    response.headers[k] = v
                return response

            except Exception as e:
                # Handle errors (timeout, connection refused, etc.)
                error_time = time.time() - start_time
                self.logger.error(f"Error forwarding request to {server}: {str(e)}")

                # Mark the server as unhealthy
                self.load_balancer.mark_unhealthy(server)

                # Update metrics
                self.load_balancer.record_request_metrics(
                    server, error_time, error=True
                )

                # Release connection if using least connections
                if hasattr(self.load_balancer, "release_connection"):
                    self.load_balancer.release_connection(server)

                return JSONResponse(content={"error": str(e)}, status_code=502)

        @self.app.get("/lb/stats")
        async def stats():
            """Get load balancer statistics."""
            metrics = self.load_balancer.get_metrics()
            return metrics

    def health_check_loop(self):
        """Periodically check the health of all servers."""
        while True:
            self.health_check()
            time.sleep(5)  # Check every 5 seconds

    def health_check(self):
        """Check the health of all servers."""
        for server in self.load_balancer.servers:
            try:
                # Simple health check - just try to connect
                start_time = time.time()
                resp = requests.get(f"{server}/health", timeout=2)
                response_time = time.time() - start_time

                # Update response time if using least response time
                if hasattr(self.load_balancer, "record_response_time"):
                    self.load_balancer.record_response_time(server, response_time)

                if resp.status_code < 500:
                    self.load_balancer.mark_healthy(server)
                else:
                    self.load_balancer.mark_unhealthy(server)

            except:
                # If we can't connect, mark the server as unhealthy
                self.load_balancer.mark_unhealthy(server)

    def run(self):
        """Run the proxy server."""
        import uvicorn

        self.logger.info(f"Starting proxy on {self.host}:{self.port}")
        uvicorn.run(self.app, host=self.host, port=self.port)
```

Overall, the load balancer aims to efficiently distribute traffic, improve system performance, and ensure high availability of backend services.
