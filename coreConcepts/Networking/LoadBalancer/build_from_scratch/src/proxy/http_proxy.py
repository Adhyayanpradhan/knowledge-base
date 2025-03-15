import time
import logging
import requests
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import threading

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("HTTPProxy")


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


# Example usage
# if __name__ == "__main__":
#     from round_robin import RoundRobinLoadBalancer

#     servers = [
#         "http://localhost:8001",
#         "http://localhost:8002",
#         "http://localhost:8003",
#     ]
#     load_balancer = RoundRobinLoadBalancer(servers)
#     proxy = LoadBalancerProxy(load_balancer)
#     proxy.run()
