from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from middleware.request_id_middleware import RequestIdMiddleware
from middleware.service_log_middleware import ServiceLogMiddleware
import logging
from logging.handlers import TimedRotatingFileHandler
from utils.dynamodb_utils import setup_dynamodb
from utils.api_utils import get_dynamodb_table
from endpoints.get_all_routes import get_all_routes
from utils.request_context import RequestIdFilter
import os
import uvicorn
import sys

sys.dont_write_bytecode = True

# Setup logging
LOG_DIR = "/var/log/pat"
LOG_FILE_APP = os.path.join(LOG_DIR, "application.log")

logger = logging.getLogger("pat_api")
logger.setLevel(logging.DEBUG)


def setup_logging():
    app_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(request_id)s - %(message)s")

    # Application log (pat_api logger)
    app_file_handler = TimedRotatingFileHandler(LOG_FILE_APP, when="midnight", backupCount=7)
    app_file_handler.setFormatter(app_formatter)
    app_file_handler.suffix = "%Y-%m-%d"
    app_file_handler.addFilter(RequestIdFilter())

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(app_formatter)
    console_handler.addFilter(RequestIdFilter())

    if not logger.hasHandlers():
        logger.addHandler(app_file_handler)
        logger.addHandler(console_handler)






app = FastAPI(
    title="PAT API",
    description="API for PAT with DynamoDB integration",
    version="1.0.0",
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(ServiceLogMiddleware)

setup_logging()
logger.info("CORS configured for local development (open for all origins).")

try:
    logger.info("Initializing DynamoDB Local.")
    dynamodb, data_table, devices_table, issues_table = setup_dynamodb(use_local=True)
except Exception as e:
    logger.error(f"Failed to set up DynamoDB: {e}")
    raise SystemExit("Critical error: Unable to initialize DynamoDB. Exiting.")

app = get_all_routes(app)

app.dependency_overrides[get_dynamodb_table] = lambda: {
    "data_table": data_table,
    "devices_table": devices_table,
    "issues_table": issues_table,
}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, log_level="info", reload=True)
