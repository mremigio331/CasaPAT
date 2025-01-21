import logging
from utils.api_utils import get_latest_info, get_all_info, generate_device_id
from botocore.exceptions import ClientError
from constants.door import DOOR_DEVICE_TYPE

logger = logging.getLogger("pat_api")


def get_latest_door_info(table, device_id: str):
    """Get the latest info for a specific door device."""
    logger.info(f"Fetching latest info for device_id: {device_id}")
    latest_info = get_latest_info(table, device_id)
    logger.info(f"Latest info: {latest_info}")

    if not latest_info:
        logger.warning(f"No latest info found for device_id: {device_id}")
        return None

    try:
        device_info = {
            "device_id": latest_info.get("DeviceID", "").split("#")[1],
            "timestamp": latest_info.get("Timestamp", "").split("#")[1],
            "current_state": latest_info.get("CurrentState"),
            "battery": float(latest_info.get("Battery", 0.0)),
        }
        logger.info(f"Latest info for device_id {device_id}: {device_info}")
        return device_info
    except (IndexError, ValueError, AttributeError) as e:
        logger.error(
            f"Error processing latest door info for device_id {device_id}: {e}"
        )
        raise ValueError(f"Error processing latest door info: {e}")


def format_all_door_info(table, device_id: str):
    """Get all info for a specific door device and format the response."""
    all_info = get_all_info(table, device_id)

    if not all_info:
        return None

    try:
        formatted_info = []
        for item in all_info:
            formatted_info.append(
                {
                    "device_id": item.get("DeviceID", "").split("#")[1],
                    "timestamp": item.get("Timestamp", "").split("#")[1],
                    "current_state": item.get("DoorStatus"),
                    "battery": float(item.get("Battery", 0.0)),
                }
            )
        return formatted_info

    except (IndexError, ValueError, AttributeError, TypeError) as e:
        logging.error(f"Error processing door info for device {device_id}: {e}")
        raise ValueError(f"Error processing data: {e}")


def add_hodor_device(table, device_name):
    """Add a new device to the DynamoDB table."""
    try:
        device_id = generate_device_id()
        logger.info(f"Generated new device ID: {device_id} for device {device_name}")

        hodor_item = {
            "DeviceID": f"DEVICE#{device_id}",
            "DeviceName": device_name,
            "DeviceType": DOOR_DEVICE_TYPE,
            "DeviceManufacturer": "Fuffly Slippers? Devices",
            "DeviceModel": "Hodor Sensor",
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
