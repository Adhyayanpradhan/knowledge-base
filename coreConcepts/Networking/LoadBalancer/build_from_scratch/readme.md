# Load Balancer

This project implements a load balancer designed to distribute incoming HTTP requests across multiple backend servers. The primary goal is to efficiently manage traffic, ensuring that requests are handled by the most appropriate server based on the selected load balancing algorithm. This helps optimize resource utilization, improve response times, and enhance the overall reliability and performance of the system.

## Key Features

- **Load Balancing Algorithms**: Supports multiple strategies, including:
  - **Round Robin**: Distributes requests evenly among servers.
  - **Weighted Round Robin**: Assigns requests based on server weights, allowing servers with higher weights to receive more requests.
  - **Least Connections**: Directs requests to the server with the fewest active connections.
  - **Least Response Time**: Chooses the server with the lowest average response time.
- **Dynamic Server Management**: Automatically marks servers as healthy or unhealthy based on their status.
- **Metrics and Logging**: Tracks various metrics such as request count, error rate, and response times.
- **Scalability and Flexibility**: Easily configurable and containerized using Docker for deployment in different environments.
- **Proxy Functionality**: Acts as an HTTP proxy, forwarding requests to backend servers based on load balancing decisions.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Docker (optional, for containerized deployment)

### Installation

1. Clone the repository:

   ```bash
   git clone git@github.com:Adhyayanpradhan/knowledge-base.git
   cd coreConcepts/Networking/LoadBalancer/build_from_scratch/
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

- Set environment variables to configure the load balancer:
  - `ALGORITHM`: The load balancing algorithm to use (e.g., `round_robin`, `least_connections`).
  - `BACKEND_SERVERS`: Comma-separated list of backend server URLs.
  - `HOST`: The host to bind the proxy to (default: `0.0.0.0`).
  - `PORT`: The port to bind the proxy to (default: `8080`).

### Running the Load Balancer

- For a Dockerized setup, build and run the Docker container:
  ```bash
  docker-compose build
  docker-compose up
  ```

## Usage

- The load balancer will listen for incoming HTTP requests and distribute them to the configured backend servers.
- Access the load balancer statistics at `/lb/stats`.

## Health Checks

- The proxy includes a health check mechanism that periodically checks the health of all servers. Servers are marked as healthy or unhealthy based on their response to a simple health check endpoint.

## Backend Server Configuration

- Backend servers are configured using environment variables for testing purposes:
  - `SERVER_ID`: Unique identifier for the server.
  - `FAILURE_RATE`: Probability of a simulated failure for testing.
  - `MIN_LATENCY` and `MAX_LATENCY`: Simulated response time range.

## Load Testing with Locust

- Locust is used for load testing the load balancer:
  - The `locustfile.py` defines user behavior and scenarios for testing.
  - Run Locust with the following command:
    ```bash
    locust -f tests/load/locustfile.py --host=http://load-balancer:8080
    ```

## Proxy Setup

- The proxy is implemented using FastAPI and handles routing of HTTP requests to backend servers.
- It includes error handling, logging, and metrics collection to ensure robust operation.
