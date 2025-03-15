import time
import random
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

# Configuration from environment variables
SERVER_ID = os.environ.get("SERVER_ID", "unknown")
FAILURE_RATE = float(os.environ.get("FAILURE_RATE", "0.05"))  # 5% failure by default
MIN_LATENCY = float(os.environ.get("MIN_LATENCY", "0.01"))  # 10ms minimum latency
MAX_LATENCY = float(os.environ.get("MAX_LATENCY", "0.5"))  # 500ms maximum latency

# Counters
request_count = 0


@app.get("/health")
async def health():
    """Health check endpoint."""
    # Sometimes randomly fail for testing purposes
    if random.random() < FAILURE_RATE:
        return JSONResponse(content={"status": "error"}, status_code=500)
    return {"status": "ok"}


@app.api_route(
    "/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"]
)
async def catch_all(path: str, request: Request):
    """Handle all requests."""
    global request_count
    request_count += 1

    # Simulate processing time
    latency = random.uniform(MIN_LATENCY, MAX_LATENCY)
    time.sleep(latency)

    # Sometimes fail for testing
    if random.random() < FAILURE_RATE:
        return JSONResponse(
            content={"error": "Internal server error", "server": SERVER_ID},
            status_code=500,
        )

    # Return information about the request
    return {
        "message": f"Request handled by {SERVER_ID}",
        "path": path,
        "method": request.method,
        "headers": dict(request.headers),
        "args": dict(request.query_params),
        "form": dict(await request.form()),
        "latency": latency,
        "request_number": request_count,
    }


@app.get("/stats")
async def stats():
    """Return server statistics."""
    return {
        "server_id": SERVER_ID,
        "request_count": request_count,
        "failure_rate": FAILURE_RATE,
        "min_latency": MIN_LATENCY,
        "max_latency": MAX_LATENCY,
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
