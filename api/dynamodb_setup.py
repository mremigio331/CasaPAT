import os
import subprocess
import requests
import tarfile
import logging
from botocore.exceptions import ClientError
import boto3
from constants.database import DATA_TABLE, DEVICE_TABLE

logger = logging.getLogger("pat_api")

DYNAMODB_LOCAL_DIR = "./dynamodb-local"
DYNAMODB_LOCAL_JAR = os.path.join(DYNAMODB_LOCAL_DIR, "DynamoDBLocal.jar")
DYNAMODB_LOCAL_DATA_DIR = os.path.join(DYNAMODB_LOCAL_DIR, "data")
DYNAMODB_LOCAL_DOWNLOAD_URL = (
    "https://s3.us-west-2.amazonaws.com/dynamodb-local/dynamodb_local_latest.tar.gz"
)


def download_dynamodb_local():
    """Download and extract DynamoDB Local if it doesn't exist."""
    logger.info(f"Looking for DynamoDB Local directory: {DYNAMODB_LOCAL_DIR}")
    if not os.path.exists(DYNAMODB_LOCAL_DIR):
        os.makedirs(DYNAMODB_LOCAL_DIR)
        logger.info(f"Created DynamoDB Local directory: {DYNAMODB_LOCAL_DIR}")

    logger.info(f"Checking for DynamoDB Local JAR at: {DYNAMODB_LOCAL_JAR}")
    if not os.path.exists(DYNAMODB_LOCAL_JAR):
        logger.info("DynamoDB Local JAR not found. Downloading...")
        response = requests.get(DYNAMODB_LOCAL_DOWNLOAD_URL, stream=True)
        if response.status_code == 200:
            tarball_path = os.path.join(
                DYNAMODB_LOCAL_DIR, "dynamodb_local_latest.tar.gz"
            )
            with open(tarball_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            logger.info("Extracting DynamoDB Local...")
            with tarfile.open(tarball_path, "r:gz") as tar:
                tar.extractall(path=DYNAMODB_LOCAL_DIR)
            os.remove(tarball_path)
            logger.info("DynamoDB Local downloaded and extracted successfully.")
        else:
            logger.error("Failed to download DynamoDB Local.")
            raise Exception("Could not download DynamoDB Local.")
    else:
        logger.info("DynamoDB Local JAR already exists. Skipping download.")


def is_dynamodb_local_running():
    """Check if DynamoDB Local is already running."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "DynamoDBLocal.jar"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode == 0:
            logger.info("DynamoDB Local is already running.")
            return True
        logger.info("DynamoDB Local is not running.")
        return False
    except Exception as e:
        logger.error(f"Failed to check if DynamoDB Local is running: {e}")
        return False


def start_dynamodb_local():
    """Start DynamoDB Local as a subprocess with persistent storage."""
    logger.info(f"Ensuring data directory exists: {DYNAMODB_LOCAL_DATA_DIR}")
    if not os.path.exists(DYNAMODB_LOCAL_DATA_DIR):
        os.makedirs(DYNAMODB_LOCAL_DATA_DIR)
        logger.info(f"Created data directory: {DYNAMODB_LOCAL_DATA_DIR}")
    else:
        logger.info(f"Data directory already exists: {DYNAMODB_LOCAL_DATA_DIR}")

    logger.info(f"Checking for DynamoDB Local JAR file at: {DYNAMODB_LOCAL_JAR}")
    if not os.path.exists(DYNAMODB_LOCAL_JAR):
        raise Exception("DynamoDB Local JAR file not found. Ensure it is downloaded.")

    if is_dynamodb_local_running():
        logger.info("DynamoDB Local is already running. Skipping startup.")
        return

    logger.info(
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
    logger.info("DynamoDB Local started successfully.")


def initialize_dynamodb(profile_name=None, use_local=False):
    """Initialize DynamoDB connection."""
    try:
        if use_local:
            logger.info("Using DynamoDB Local.")
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
            logger.info(f"Using AWS profile: {profile_name}")
            session = boto3.Session(profile_name=profile_name)
            dynamodb = session.resource("dynamodb", region_name="us-west-2")

        logger.info("DynamoDB session initialized.")
        return dynamodb
    except Exception as e:
        logger.error(f"Failed to initialize DynamoDB: {e}")
        raise SystemExit("Critical error: Unable to initialize DynamoDB. Exiting.")


def create_dynamodb_table(dynamodb, table_name, key_schema, attribute_definitions):
    """Create a DynamoDB table with given schema."""
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            BillingMode="PAY_PER_REQUEST",
        )
        table.meta.client.get_waiter("table_exists").wait(TableName=table_name)
        logger.info(f"Table '{table_name}' created successfully.")
        return table
    except Exception as e:
        logger.error(f"Failed to create table '{table_name}': {e}")
        raise


def ensure_data_table_exists(dynamodb):
    """Ensure the PAT data table exists."""
    try:
        table = dynamodb.Table(DATA_TABLE)
        table.load()
        logger.info(f"Table '{DATA_TABLE}' already exists.")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            logger.info("Table 'PATData' not found. Creating...")
            return create_dynamodb_table(
                dynamodb,
                DATA_TABLE,
                [
                    {"AttributeName": "DeviceID", "KeyType": "HASH"},
                    {"AttributeName": "Timestamp", "KeyType": "RANGE"},
                ],
                [
                    {"AttributeName": "DeviceID", "AttributeType": "S"},
                    {"AttributeName": "Timestamp", "AttributeType": "S"},
                ],
            )
        else:
            logger.error(f"Error accessing table: {e}")
            raise


def ensure_devices_table_exists(dynamodb):
    """Ensure the PAT devices table exists."""
    try:
        table = dynamodb.Table(DEVICE_TABLE)
        table.load()
        logger.info(f"Table '{DEVICE_TABLE}' already exists.")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            logger.info(f"Table '{DEVICE_TABLE}' not found. Creating...")
            return create_dynamodb_table(
                dynamodb,
                DEVICE_TABLE,
                [
                    {"AttributeName": "DeviceID", "KeyType": "HASH"},
                    {"AttributeName": "DeviceType", "KeyType": "RANGE"},
                ],
                [
                    {"AttributeName": "DeviceID", "AttributeType": "S"},
                    {"AttributeName": "DeviceType", "AttributeType": "S"},
                ],
            )
        else:
            logger.error(f"Error accessing table: {e}")
            raise


def setup_dynamodb(profile_name=None, use_local=True):
    """Set up DynamoDB and ensure tables exist."""
    dynamodb = initialize_dynamodb(profile_name, use_local)
    data_table = ensure_data_table_exists(dynamodb)
    devices_table = ensure_devices_table_exists(dynamodb)
    return dynamodb, data_table, devices_table
