import os
import subprocess
import requests
import tarfile
import logging
from botocore.exceptions import ClientError
import boto3


DYNAMODB_LOCAL_DIR = "./dynamodb-local"
DYNAMODB_LOCAL_JAR = os.path.join(DYNAMODB_LOCAL_DIR, "DynamoDBLocal.jar")
DYNAMODB_LOCAL_DATA_DIR = os.path.join(DYNAMODB_LOCAL_DIR, "data")
DYNAMODB_LOCAL_DOWNLOAD_URL = (
    "https://s3.us-west-2.amazonaws.com/dynamodb-local/dynamodb_local_latest.tar.gz"
)


def download_dynamodb_local():
    """Download and extract DynamoDB Local if it doesn't exist."""
    logging.info(f"Looking for DynamoDB Local directory: {DYNAMODB_LOCAL_DIR}")
    if not os.path.exists(DYNAMODB_LOCAL_DIR):
        os.makedirs(DYNAMODB_LOCAL_DIR)
        logging.info(f"Created DynamoDB Local directory: {DYNAMODB_LOCAL_DIR}")

    logging.info(f"Checking for DynamoDB Local JAR at: {DYNAMODB_LOCAL_JAR}")
    if not os.path.exists(DYNAMODB_LOCAL_JAR):
        logging.info("DynamoDB Local JAR not found. Downloading...")
        response = requests.get(DYNAMODB_LOCAL_DOWNLOAD_URL, stream=True)
        if response.status_code == 200:
            tarball_path = os.path.join(
                DYNAMODB_LOCAL_DIR, "dynamodb_local_latest.tar.gz"
            )
            with open(tarball_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            logging.info("Extracting DynamoDB Local...")
            with tarfile.open(tarball_path, "r:gz") as tar:
                tar.extractall(path=DYNAMODB_LOCAL_DIR)
            os.remove(tarball_path)
            logging.info("DynamoDB Local downloaded and extracted successfully.")
        else:
            logging.error("Failed to download DynamoDB Local.")
            raise Exception("Could not download DynamoDB Local.")
    else:
        logging.info("DynamoDB Local JAR already exists. Skipping download.")


def is_dynamodb_local_running():
    """Check if DynamoDB Local is already running."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "DynamoDBLocal.jar"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode == 0:
            logging.info("DynamoDB Local is already running.")
            return True
        logging.info("DynamoDB Local is not running.")
        return False
    except Exception as e:
        logging.error(f"Failed to check if DynamoDB Local is running: {e}")
        return False


def start_dynamodb_local():
    """Start DynamoDB Local as a subprocess with persistent storage."""
    logging.info(f"Ensuring data directory exists: {DYNAMODB_LOCAL_DATA_DIR}")
    if not os.path.exists(DYNAMODB_LOCAL_DATA_DIR):
        os.makedirs(DYNAMODB_LOCAL_DATA_DIR)
        logging.info(f"Created data directory: {DYNAMODB_LOCAL_DATA_DIR}")
    else:
        logging.info(f"Data directory already exists: {DYNAMODB_LOCAL_DATA_DIR}")

    logging.info(f"Checking for DynamoDB Local JAR file at: {DYNAMODB_LOCAL_JAR}")
    if not os.path.exists(DYNAMODB_LOCAL_JAR):
        raise Exception("DynamoDB Local JAR file not found. Ensure it is downloaded.")

    if is_dynamodb_local_running():
        logging.info("DynamoDB Local is already running. Skipping startup.")
        return

    logging.info(
        f"Starting DynamoDB Local with data directory at: {DYNAMODB_LOCAL_DATA_DIR}"
    )
    subprocess.Popen(
        [
            "java",
            "-Djava.library.path=./dynamodb-local/DynamoDBLocal_lib",
            "-jar",
            DYNAMODB_LOCAL_JAR,
            "-sharedDb",
            "-dbPath",
            DYNAMODB_LOCAL_DATA_DIR,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    logging.info("DynamoDB Local started successfully.")


def initialize_dynamodb(profile_name=None, use_local=False):
    """Initialize DynamoDB connection."""
    try:
        if use_local:
            logging.info("Using DynamoDB Local.")
            download_dynamodb_local()
            start_dynamodb_local()

            session = boto3.Session(
                aws_access_key_id="fakeAccessKey", aws_secret_access_key="fakeSecretKey"
            )
            dynamodb = session.resource(
                "dynamodb",
                region_name="us-west-2",
                endpoint_url="http://localhost:8000",
            )
        else:
            session = boto3.Session(profile_name=profile_name)
            dynamodb = session.resource("dynamodb", region_name="us-west-2")

        logging.info("DynamoDB session initialized.")
        return dynamodb
    except Exception as e:
        logging.error(f"Failed to initialize DynamoDB: {e}")
        raise SystemExit("Critical error: Unable to initialize DynamoDB. Exiting.")


def ensure_table_exists(dynamodb):
    """Ensure the PAT table exists."""
    try:
        table = dynamodb.Table("PATData")
        table.load()
        logging.info("Table 'PATData' already exists.")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            logging.info("Table 'PATData' not found. Creating...")
            table = dynamodb.create_table(
                TableName="PATData",
                KeySchema=[
                    {"AttributeName": "DeviceID", "KeyType": "HASH"},
                    {"AttributeName": "Timestamp", "KeyType": "RANGE"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "DeviceID", "AttributeType": "S"},
                    {"AttributeName": "Timestamp", "AttributeType": "S"},
                ],
                BillingMode="PAY_PER_REQUEST",
            )
            table.meta.client.get_waiter("table_exists").wait(TableName="PATData")
            logging.info("Table 'PATData' created successfully.")
        else:
            logging.error(f"Error accessing table: {e}")
            raise SystemExit("Critical error: Unable to access DynamoDB. Exiting.")
    return table


def setup_dynamodb(profile_name=None, use_local=True):
    """Set up DynamoDB and ensure table exists."""
    dynamodb = initialize_dynamodb(profile_name, use_local)
    table = ensure_table_exists(dynamodb)
    return dynamodb, table
