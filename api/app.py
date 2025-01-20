from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
from logging.handlers import TimedRotatingFileHandler
from dynamodb_setup import setup_dynamodb
from utils.api_utils import get_dynamodb_table
from endpoints.get_all_routes import get_all_routes
import os
import uvicorn
import sys

sys.dont_write_bytecode = True

# Setup logging directory and file
LOG_DIR = "/var/log/pat"
LOG_FILE_API = os.path.join(LOG_DIR, "pat_api.log")

# Configure logger
logger = logging.getLogger("pat_api")
logger.setLevel(logging.INFO)

# Ensure the log directory exists
try:
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        logger.info(f"Log directory created at {LOG_DIR}.")
except Exception as e:
    raise SystemExit(f"Critical error: Unable to create log directory: {e}")

# Configure file handler for logging
handler = TimedRotatingFileHandler(LOG_FILE_API, when="midnight", backupCount=7)
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
handler.suffix = "%Y-%m-%d"
logger.addHandler(handler)

# Create FastAPI app
app = FastAPI(
    title="PAT API",
    description="API for PAT with DynamoDB integration",
    version="1.0.0",
)


@app.middleware("http")
async def log_request_info(request: Request, call_next):
    client_host = request.client.host  # Get the requester's hostname/IP
    request_method = request.method
    request_url = request.url.path

    # Read and decode request body safely
    try:
        body = await request.body()
        payload = body.decode() if body else "{}"  # Handle empty body gracefully
    except Exception as e:
        payload = f"Error reading body: {e}"

    logger.info(
        f"Incoming request from {client_host}: {request_method} {request_url}, "
        f"Payload: {payload}"
    )

    # Create a new request object with the body to avoid reading issues
    request = Request(request.scope, receive=lambda: body)

    response = await call_next(request)  # Pass request to the next middleware/handler
    return response


# Configure CORS (Open for all origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open for all origins (adjust for production use)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS is open for all origins. This is intended for local use only.")

# Setup DynamoDB (Local)
try:
    logger.info("Initializing DynamoDB Local.")
    dynamodb, table = setup_dynamodb(use_local=True)
except Exception as e:
    logger.error(f"Failed to set up DynamoDB: {e}")
    raise SystemExit("Critical error: Unable to initialize DynamoDB. Exiting.")

# Register all endpoints using the get_all_routes utility function
app = get_all_routes(app)

# Override the dependency to provide the table instance globally
app.dependency_overrides[get_dynamodb_table] = lambda: table

if __name__ == "__main__":
    debug_mode = True
    uvicorn.run(
        "app:app", host="pat.local", port=5000, log_level="info", reload=debug_mode
    )
