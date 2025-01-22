import boto3
import logging
from fastapi import Depends, HTTPException
from boto3.dynamodb.conditions import Key, Attr

from typing import Literal
import random
import string

logger = logging.getLogger("pat_api")


def get_dynamodb_table(table_name: Literal["PATData", "PATDevices"]):
    """Returns the specified DynamoDB table instance connected to the local environment."""

    dynamodb = boto3.resource(
        "dynamodb",
        region_name="us-west-2",
        endpoint_url="http://localhost:8000",
        aws_access_key_id="fakeAccessKey",
        aws_secret_access_key="fakeSecretKey",
    )

    try:
        table = dynamodb.Table(table_name)
        return table
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing table: {e}")


def get_table(table=Depends(get_dynamodb_table)):
    if not table:
        logger.error("DynamoDB table is unavailable.")
        raise HTTPException(status_code=500, detail="DynamoDB is unavailable")
    return table


def unique_device_names(table, device_type):
    """Fetch all unique device IDs from the DynamoDB table for a specific device type."""
    try:
        unique_names = set()

        # Scan with filter expression to get only specific device type
        response = table.scan(
            ProjectionExpression="DeviceID, DeviceName, DeviceType",
            FilterExpression="DeviceType = :device_type",
            ExpressionAttributeValues={":device_type": device_type},
        )

        logger.info(
            f"Found a totoal of {len(response.get('Items', []))} items for device type '{device_type}'"
        )
        logger.info(f"Items: {response.get('Items', [])}")

        # Collect unique DeviceNames
        for item in response.get("Items", []):
            logger.info(f"Found DeviceID: {item}")
            device_name = item.get("DeviceName")
            unique_names.add(device_name)

        # Handle pagination if LastEvaluatedKey exists
        while "LastEvaluatedKey" in response:
            response = table.scan(
                ProjectionExpression="DeviceID",
                FilterExpression="DeviceType = :device_type",
                ExpressionAttributeValues={":device_type": device_type},
                ExclusiveStartKey=response["LastEvaluatedKey"],
            )
            for item in response.get("Items", []):
                device_name = item["DeviceName"]
                logging.info(f"Found DeviceID: {device_name}")
                unique_names.add(device_name)

        logging.info(
            f"Unique device names for device type '{device_type}': {unique_names}"
        )
        return list(unique_names)

    except Exception as e:
        logging.error(f"Error fetching unique device IDs: {e}")
        raise


def get_latest_info(table, device_id):
    """Fetch the latest entry for a specific device."""
    try:
        response = table.query(
            KeyConditionExpression=Key("DeviceID").eq(device_id),
            ScanIndexForward=False,
            Limit=1,
        )
        if "Items" in response and response["Items"]:
            item = response["Items"][0]
            return item

        else:
            logging.info(f"No entries found for device {device_id}.")
            return None
    except Exception as e:
        logging.error(f"Error fetching latest info for device {device_id}: {e}")
        raise


def get_device_info(table, device_name):
    """Fetch all entries for a specific device from the DynamoDB table."""
    try:
        logging.info(f"Fetching entries for device name: {device_name}")
        items = []
        last_evaluated_key = None

        while True:
            # Scan the table with filter expression
            scan_params = {"FilterExpression": Attr("DeviceName").eq(device_name)}
            if last_evaluated_key:
                scan_params["ExclusiveStartKey"] = last_evaluated_key

            response = table.scan(**scan_params)

            # Append matching items
            items.extend(response.get("Items", []))

            # Check if there's more data to be scanned
            last_evaluated_key = response.get("LastEvaluatedKey")
            if not last_evaluated_key:
                break

        if len(items) == 1:
            logging.info(f"Found the following info for {device_name}: {items[0]}")
            return items[0]
        elif len(items) > 1:
            logging.warning(f"Multiple entries found for {device_name}: {items}")
            return items[0]
        else:
            logging.warning(f"No entries found for device name: {device_name}")
            return []

    except Exception as e:
        logging.error(f"Error fetching all info for device name {device_name}: {e}")
        raise


def get_all_info(table, device_id):
    """Fetch all entries for a specific device from the DynamoDB table."""
    try:
        response = table.scan(FilterExpression=Attr("DeviceID").eq(device_id))
        logging.info(f"response: {response}")
        if response.get("Items"):
            return response["Items"]
        else:
            logging.warning(f"No entries found for device ID: {device_id}")
            return []
    except Exception as e:
        logging.error(f"Error fetching all info for device ID {device_id}: {e}")
        raise


def generate_device_id():
    """Generate a random 8-character alphanumeric device ID."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


def delete_device_entries_from_data_table(table, device_id):
    """Delete all entries with the given device_id from the PATData table (DeviceID, Timestamp)."""

    try:
        logger.info(f"Deleting device {device_id} from PATData table")

        # Scan for all matching entries with DeviceID
        response = table.scan(FilterExpression=Attr("DeviceID").eq(device_id))

        items = response.get("Items", [])
        if not items:
            logger.warning(
                f"No entries found for DeviceID: {device_id} in PATData table"
            )
            return 0

        # Delete each item using composite key (DeviceID + Timestamp)
        for item in items:
            partition_key_value = item["DeviceID"]
            sort_key_value = item["Timestamp"]  # Ensure correct attribute name

            key_to_delete = {
                "DeviceID": partition_key_value,
                "Timestamp": sort_key_value,
            }

            table.delete_item(Key=key_to_delete)
            logger.info(f"Deleted item with Timestamp: {sort_key_value}")

        logger.info(f"Successfully deleted {len(items)} items from PATData table")
        return len(items)

    except Exception as e:
        logger.error(f"Error deleting device {device_id} from PATData table: {e}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error deleting from PATData"
        )


def delete_device_entries_from_devices_table(table, device_id):
    """Delete all entries with the given device_id from the PATDevices table (DeviceID, DeviceName)."""

    try:
        logger.info(f"Deleting device {device_id} from PATDevices table")

        # Scan for all matching entries with DeviceID
        response = table.scan(FilterExpression=Attr("DeviceID").eq(device_id))

        items = response.get("Items", [])
        if not items:
            logger.warning(
                f"No entries found for DeviceID: {device_id} in PATDevices table"
            )
            return 0

        # Delete each item using composite key (DeviceID + DeviceName)
        for item in items:
            partition_key_value = item["DeviceID"]
            sort_key_value = item["DeviceName"]  # Ensure correct attribute name

            key_to_delete = {
                "DeviceID": partition_key_value,
                "DeviceName": sort_key_value,
            }

            table.delete_item(Key=key_to_delete)
            logger.info(f"Deleted item with DeviceName: {sort_key_value}")

        logger.info(f"Successfully deleted {len(items)} items from PATDevices table")
        return len(items)

    except Exception as e:
        logger.error(f"Error deleting device {device_id} from PATDevices table: {e}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error deleting from PATDevices"
        )


def craft_delete_resposne(device_id, device_deleted_count, data_deleted_count):
    """Craft a response message for the delete_device endpoint."""

    message = f"Deleted {device_deleted_count} devices and {data_deleted_count} data entries for device {device_id}."

    if device_deleted_count > 1:
        message += " Not sure why you had multiple devices with the same ID."

    return message
