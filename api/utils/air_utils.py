from decimal import Decimal
from boto3.dynamodb.conditions import Key
import logging
import json
from utils.api_utils import get_latest_info, get_all_info, generate_device_id
from botocore.exceptions import ClientError
from constants.air import AIR_QUALITY_DEVICE_TYPE, PM10_INFO, PM25_INFO
from datetime import datetime, timedelta, timezone
from decimal import Decimal

logger = logging.getLogger("pat_api")


def get_air_quality_levels():
    return {"PM2.5": PM25_INFO, "PM10": PM10_INFO}


def get_air_quality_info(value, pm_type_levels):
    for level in pm_type_levels:
        min_value, max_value = map(float, level["range"].split(" to "))
        if min_value <= value <= max_value:
            return level["message"], level["code"]
    return "Unknown", 0


def normalize_item(item):
    """Normalize DynamoDB item for JSON response."""
    return {
        k: str(v) if isinstance(v, (int, float, Decimal)) else v
        for k, v in item.items()
    }


def convert_decimals_to_floats(data):
    """Recursively convert Decimal values to float for JSON serialization."""
    if isinstance(data, list):
        return [convert_decimals_to_floats(item) for item in data]
    elif isinstance(data, dict):
        return {k: convert_decimals_to_floats(v) for k, v in data.items()}
    elif isinstance(data, Decimal):
        return float(data)  # Convert Decimal to float
    return data


def staleness_check(timestamp_str: str) -> tuple[bool, int]:
    """Check if the given timestamp is more than 20 minutes old and return its age in seconds.

    Args:
        timestamp_str (str): The timestamp string in format 'YYYY-MM-DDTHH:MM:SSZ'.

    Returns:
        tuple: (bool, int) where:
            - bool: True if the timestamp is older than 20 minutes, False otherwise.
            - int: The age of the timestamp in seconds.
    """
    try:
        # Convert the timestamp string to a datetime object (assuming UTC time)
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )

        # Get the current time in UTC
        current_time = datetime.now(timezone.utc)

        # Calculate the time difference
        time_difference = current_time - timestamp

        # Get the age in seconds
        age_in_seconds = int(time_difference.total_seconds())

        # Check if the timestamp is older than 20 minutes
        is_older = time_difference > timedelta(minutes=20)

        return is_older, age_in_seconds

    except ValueError:
        raise ValueError("Invalid timestamp format. Expected 'YYYY-MM-DDTHH:MM:SSZ'")


def get_latest_air_quality_info(table, device_id):
    """Fetch the latest entry for a specific device."""
    logger.debug(f"Fetching latest info for device_id: {device_id}")
    latest_info = get_latest_info(table, device_id)

    if not latest_info:
        logger.debug(f"No latest info found for device_id: {device_id}")
        return None

    try:
        pm25_value = float(latest_info.get("PM25", 0.0))
        pm10_value = float(latest_info.get("PM10", 0.0))
        latest_info["PM25"] = pm25_value
        latest_info["PM25"] = pm25_value
        if pm25_value is not None:
            message, code = get_air_quality_info(
                pm25_value, get_air_quality_levels()["PM2.5"]
            )
            latest_info["message"] = message
            latest_info["code"] = int(code)
            logger.debug(f"Message: {message}. Code: {code}")

        elif pm10_value is not None:
            message, code = get_air_quality_info(
                pm10_value, get_air_quality_levels()["PM10"]
            )
            latest_info["message"] = message
            latest_info["code"] = int(code)
            logger.debug(f"Message: {message}. Code: {code}")

        else:
            latest_info["message"] = "Unknown"
            latest_info["code"] = 0
            logger.debug("No message or code identified")
    except Exception as e:
        logger.error(
            f"Error processing latest air quality info for device_id {device_id}: {e}"
        )
        raise ValueError(f"Error processing latest air quality info: {e}")

    try:
        time_stamp = latest_info.get("Timestamp")
        stale, age = staleness_check(time_stamp)
        latest_info["staleness"] = stale
        latest_info["age"] = age

    except Exception as e:
        logger.error(f"Error processing staleness check for device_id {device_id}: {e}")
        raise ValueError(f"Error processing staleness check: {e}")

    return convert_decimals_to_floats(latest_info)


def add_walle_device(table, device_name):
    """Add a new device to the DynamoDB table."""
    try:
        device_id = generate_device_id()
        logger.debug(f"Generated new device ID: {device_id} for device {device_name}")

        hodor_item = {
            "DeviceID": f"DEVICE#{device_id}",
            "DeviceName": device_name,
            "DeviceType": AIR_QUALITY_DEVICE_TYPE,
            "DeviceManufacturer": "Fuffly Slippers? Devices",
            "DeviceModel": "WALL-E Sensor",
        }
        logger.debug(f"Adding item to DynamoDB")

        response = table.put_item(Item=hodor_item)
        logger.debug(f"Device added successfully")

        logger.info(
            f"Added new device with ID {device_id} and name {device_name} to table."
        )
        return hodor_item

    except ClientError as e:
        logger.error(
            f"ClientError adding new device {device_name} to table: {e.response['Error']['Message']}"
        )
        raise
    except Exception as e:
        logger.error(f"Unexpected error adding new device {device_name} to table: {e}")
        raise


def format_full_air_info(table, device_id: str):
    """Get all info for a specific door device and format the response."""
    logger.debug(f"Starting formatting for device_id: {device_id}")
    all_info = get_all_info(table, device_id)

    if not all_info:
        return None

    try:
        formatted_info = []
        for item in all_info:
            logger.debug(f"Processing item for {device_id}")
            formatted_info.append(
                {
                    "device_id": item.get("DeviceID", "").split("#")[1],
                    "event_id": item.get("EventID", "").split("#")[1],
                    "timestamp": item.get("Timestamp", ""),
                    "pm25": float(item.get("PM25", 0.0)),
                    "pm10": float(item.get("PM10", 0.0)),
                }
            )
        return formatted_info

    except (IndexError, ValueError, AttributeError, TypeError) as e:
        logger.error(f"Error processing air info for device {device_id}: {e}")
        raise ValueError(f"Error processing data: {e}")
