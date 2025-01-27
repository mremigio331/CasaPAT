from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
from logging.handlers import TimedRotatingFileHandler
from utils.dynamodb_utils import setup_dynamodb
from utils.api_utils import get_dynamodb_table
from endpoints.get_all_routes import get_all_routes
import os
import uvicorn
import sys

sys.dont_write_bytecode = True

# Setup logging
LOG_DIR = "/var/log/pat"
LOG_FILE_API = os.path.join(LOG_DIR, "pat_api.log")

logger = logging.getLogger("pat_api")
logger.setLevel(logging.INFO)


def setup_logging():
    """Ensure the log directory exists and set up logging handlers."""
    try:
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
            logger.info(f"Log directory created at {LOG_DIR}.")
    except Exception as e:
        raise SystemExit(f"Critical error: Unable to create log directory: {e}")

    # File Handler
    file_handler = TimedRotatingFileHandler(
        LOG_FILE_API, when="midnight", backupCount=7
    )
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    file_handler.suffix = "%Y-%m-%d"

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )

    # Add handlers if not already present
    if not logger.hasHandlers():
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)


setup_logging()

app = FastAPI(
    title="PAT API",
    description="API for PAT with DynamoDB integration",
    version="1.0.0",
)


@app.middleware("http")
async def log_request_info(request: Request, call_next):
    client_host = request.client.host
    request_method = request.method
    request_url = request.url.path

    body = await request.body()
    payload = body.decode("utf-8") if body else "{}"

    logger.info(
        f"Incoming request from {client_host}: {request_method} {request_url}, "
        f"Payload: {payload}"
    )

    response = await call_next(request)
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS configured for local development (open for all origins).")

try:
    logger.info("Initializing DynamoDB Local.")
    dynamodb, data_table, devices_table = setup_dynamodb(use_local=True)
except Exception as e:
    logger.error(f"Failed to set up DynamoDB: {e}")
    raise SystemExit("Critical error: Unable to initialize DynamoDB. Exiting.")

app = get_all_routes(app)

app.dependency_overrides[get_dynamodb_table] = lambda: {
    "data_table": data_table,
    "devices_table": devices_table,
}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, log_level="info", reload=True)
