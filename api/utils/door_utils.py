import logging
import requests
import json
from utils.api_utils import get_latest_info, get_all_info, generate_device_id
from botocore.exceptions import ClientError
from constants.door import DOOR_DEVICE_TYPE

logger = logging.getLogger("pat_api")


def get_latest_door_info(table, device_id: str):
    """Get the latest info for a specific door device."""
    logger.debug(f"Fetching latest info for device_id: {device_id}")
    latest_info = get_latest_info(table, device_id)

    if not latest_info:
        logger.debug(f"No latest info found for device_id: {device_id}")
        return None

    try:
        device_info = {
            "device_id": latest_info.get("DeviceID", "").split("#")[1],
            "event_id": latest_info.get("EventID", "").split("#")[1],
            "timestamp": latest_info.get("Timestamp", ""),
            "door_status": latest_info.get("DoorStatus"),
            "battery": float(latest_info.get("Battery", 0.0)),
        }
        logger.debug(f"Latest info found for device_id {device_id}")
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
                    "door_status": item.get("DoorStatus"),
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
        logger.debug(f"Generated new device ID: {device_id} for device {device_name}")

        hodor_item = {
            "DeviceID": f"DEVICE#{device_id}",
            "DeviceName": device_name,
            "DeviceType": DOOR_DEVICE_TYPE,
            "DeviceManufacturer": "Fuffly Slippers? Devices",
            "DeviceModel": "Hodor Sensor",
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


def store_webhook(table, webhook_url: str, device_name: str = None):
    """Store a webhook URL in DynamoDB for door state notifications."""
    try:
        webhook_id = generate_device_id()
        webhook_item = {
            "WebhookID": f"WEBHOOK#{webhook_id}",
            "WebhookURL": webhook_url,
            "DeviceName": device_name if device_name else "ALL",
            "Active": True,
        }
        logger.debug(f"Storing webhook: {json.dumps(webhook_item, default=str)}")
        table.put_item(Item=webhook_item)
        logger.info(f"Webhook registered successfully: {webhook_url}")
        return webhook_item
    except Exception as e:
        logger.error(f"Error storing webhook: {e}")
        raise


def get_active_webhooks(table, device_name: str = None):
    """Retrieve all active webhooks from DynamoDB."""
    try:
        response = table.scan(
            FilterExpression="Active = :active",
            ExpressionAttributeValues={":active": True},
        )
        webhooks = response.get("Items", [])

        # Filter by device_name if specified
        if device_name:
            webhooks = [
                w
                for w in webhooks
                if w.get("DeviceName") == device_name or w.get("DeviceName") == "ALL"
            ]

        logger.debug(f"Found {len(webhooks)} active webhooks")
        return webhooks
    except Exception as e:
        logger.error(f"Error retrieving webhooks: {e}")
        return []


def trigger_webhooks(table, door_data: dict):
    """Trigger all registered webhooks with door state data."""
    try:
        device_name = door_data.get("device_name")
        webhooks = get_active_webhooks(table, device_name)

        if not webhooks:
            logger.debug(f"No webhooks registered for device {device_name}")
            return

        payload = {
            "device_name": device_name,
            "device_id": door_data.get("device_id"),
            "timestamp": door_data.get("timestamp"),
            "door_status": door_data.get("door_status"),
            "battery": door_data.get("battery"),
        }

        for webhook in webhooks:
            webhook_url = webhook.get("WebhookURL")
            try:
                logger.debug(f"Triggering webhook: {webhook_url}")
                response = requests.post(
                    webhook_url,
                    json=payload,
                    timeout=5,
                    headers={"Content-Type": "application/json"},
                )
                logger.info(
                    f"Webhook triggered successfully: {webhook_url} (Status: {response.status_code})"
                )
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to trigger webhook {webhook_url}: {e}")
    except Exception as e:
        logger.error(f"Error triggering webhooks: {e}")
