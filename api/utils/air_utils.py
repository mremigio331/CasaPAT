from decimal import Decimal
from boto3.dynamodb.conditions import Key
import logging
import json
from utils.api_utils import get_latest_info, get_all_info, generate_device_id
from botocore.exceptions import ClientError
from constants.air import AIR_QUALITY_DEVICE_TYPE

logger = logging.getLogger("pat_api")


def get_air_quality_levels():
    with open("air_quality_levels.json", "r") as json_file:
        return json.load(json_file)


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


def convert_floats_to_decimals(data):
    """Recursively convert float values to Decimal."""
    if isinstance(data, list):
        return [convert_floats_to_decimals(item) for item in data]
    elif isinstance(data, dict):
        return {k: convert_floats_to_decimals(v) for k, v in data.items()}
    elif isinstance(data, float):
        return Decimal(str(data))
    return data


def get_latest_air_quality_info(table, device_id):
    """Fetch the latest entry for a specific device."""
    try:
        response = table.query(
            KeyConditionExpression=Key("DeviceID").eq(device_id),
            ScanIndexForward=False,
            Limit=1,
        )
        if "Items" in response and response["Items"]:
            item = response["Items"][0]
            pm25_value = item.get("PM25")
            pm10_value = item.get("PM10")

            if pm25_value is not None:
                message, code = get_air_quality_info(
                    pm25_value, get_air_quality_levels()["PM2.5"]
                )
                item["message"] = message
                item["code"] = int(code)
                logger.info(f"Message: {message}. Code: {code}")

            elif pm10_value is not None:
                message, code = get_air_quality_info(
                    pm10_value, get_air_quality_levels()["PM10"]
                )
                item["message"] = message
                item["code"] = int(code)
                logger.info(f"Message: {message}. Code: {code}")

            else:
                item["message"] = "Unknown"
                item["code"] = 0
                logger.info("No message or code identified")

            return item
        else:
            logger.info(f"No entries found for device {device_id}.")
            return None
    except Exception as e:
        logger.error(f"Error fetching latest info for device {device_id}: {e}")
        raise


def add_walle_device(table, device_name):
    """Add a new device to the DynamoDB table."""
    try:
        device_id = generate_device_id()
        logger.info(f"Generated new device ID: {device_id} for device {device_name}")

        hodor_item = {
            "DeviceID": f"DEVICE#{device_id}",
            "DeviceName": device_name,
            "DeviceType": AIR_QUALITY_DEVICE_TYPE,
            "DeviceManufacturer": "Fuffly Slippers? Devices",
            "DeviceModel": "WALL-E Sensor",
        }
        logger.info(f"Adding item to DynamoDB: {hodor_item}")

        response = table.put_item(Item=hodor_item)
        logger.info(f"DynamoDB put_item response: {response}")

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
