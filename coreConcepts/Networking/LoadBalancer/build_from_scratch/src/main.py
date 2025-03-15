# src/main.py
import os
import logging
from src.proxy.http_proxy import LoadBalancerProxy
from src.algorithms.round_robin import RoundRobinLoadBalancer
from src.algorithms.weighted_round_robin import WeightedRoundRobinLoadBalancer
from src.algorithms.least_connection import LeastConnectionsLoadBalancer
from src.algorithms.least_response_time import LeastResponseTimeLoadBalancer

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("main")


def create_load_balancer(algorithm, servers):
    """
    Create a load balancer with the specified algorithm.

    Args:
        algorithm (str): The load balancing algorithm to use.
        servers (list): List of server URLs.

    Returns:
        BaseLoadBalancer: The load balancer instance.
    """
    algorithm = algorithm.lower()

    if algorithm == "round_robin":
        logger.info("Entering round robin")
        return RoundRobinLoadBalancer(servers)
    elif algorithm == "weighted_round_robin":
        # Example weights - in a real system these would be configured
        weights = {server: i + 1 for i, server in enumerate(servers)}
        logger.info("Entering weighted round robin")
        
        return WeightedRoundRobinLoadBalancer(servers, weights)
    elif algorithm == "least_connections":
        logger.info("Entering least connections")
        
        return LeastConnectionsLoadBalancer(servers)
    elif algorithm == "least_response_time":
        logger.info("Entering rleast response time")
        
        return LeastResponseTimeLoadBalancer(servers)
    else:
        logger.warning(f"Unknown algorithm: {algorithm}, defaulting to round_robin")
        return RoundRobinLoadBalancer(servers)


def main():
    # Get configuration from environment
    algorithm = os.environ.get("ALGORITHM", "round_robin")
    backend_servers_str = os.environ.get(
        "BACKEND_SERVERS", "http://localhost:5001,http://localhost:5002"
    )
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8080))

    # Parse backend servers
    backend_servers = backend_servers_str.split(",")

    logger.info(f"Starting load balancer with algorithm: {algorithm}")
    logger.info(f"Backend servers: {backend_servers}")

    # Create the load balancer
    load_balancer = create_load_balancer(algorithm, backend_servers)

    # Create and run the proxy
    proxy = LoadBalancerProxy(load_balancer, host, port)
    proxy.run()


if __name__ == "__main__":
    main()
