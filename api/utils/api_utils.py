import boto3
import logging
from fastapi import Depends, HTTPException
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

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
            KeyConditionExpression=Key("DeviceID").eq(f"DEVICE#{device_id}"),
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


def get_all_info(table, device_id):
    """Fetch all entries for a specific device."""
    try:
        response = table.query(
            KeyConditionExpression=Key("DeviceID").eq(f"DEVICE#{device_id}"),
            ScanIndexForward=False,
        )
        if "Items" in response and response["Items"]:
            return response["Items"]
        else:
            logging.info(f"No entries found for device {device_id}.")
            return None
    except Exception as e:
        logging.error(f"Error fetching all info for device {device_id}: {e}")
        raise


def generate_device_id():
    """Generate a random 8-character alphanumeric device ID."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


def add_device(table, device_name, device_type):
    """Add a new device to the DynamoDB table."""
    try:
        device_id = generate_device_id()
        logger.info(f"Generated new device ID: {device_id} for device {device_name}")

        item = {
            "DeviceID": f"DEVICE#{device_id}",
            "DeviceName": device_name,
            "DeviceType": device_type,
        }
        logger.info(f"Adding item to DynamoDB: {item}")

        response = table.put_item(Item=item)
        logger.info(f"DynamoDB put_item response: {response}")

        logger.info(
            f"Added new device with ID {device_id} and name {device_name} to table."
        )
        return device_id

    except ClientError as e:
        logger.error(
            f"ClientError adding new device {device_name} to table: {e.response['Error']['Message']}"
        )
        raise
    except Exception as e:
        logger.error(f"Unexpected error adding new device {device_name} to table: {e}")
        raise
