import boto3
import logging
from fastapi import Depends, HTTPException
from boto3.dynamodb.conditions import Key
from typing import Literal

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


def unique_device_ids(table, device_type):
    """Fetch all unique device IDs from the DynamoDB table for a specific device type."""
    try:
        unique_ids = set()

        # Scan with filter expression to get only specific device type
        response = table.scan(
            ProjectionExpression="DeviceID",
            FilterExpression="DeviceType = :device_type",
            ExpressionAttributeValues={":device_type": device_type},
        )

        # Collect unique DeviceIDs
        for item in response.get("Items", []):
            device_id = item["DeviceID"]
            logging.info(f"Found DeviceID: {device_id}")
            unique_ids.add(device_id)

        # Handle pagination if LastEvaluatedKey exists
        while "LastEvaluatedKey" in response:
            response = table.scan(
                ProjectionExpression="DeviceID",
                FilterExpression="DeviceType = :device_type",
                ExpressionAttributeValues={":device_type": device_type},
                ExclusiveStartKey=response["LastEvaluatedKey"],
            )
            for item in response.get("Items", []):
                device_id = item["DeviceID"]
                logging.info(f"Found DeviceID: {device_id}")
                unique_ids.add(device_id)

        # Split DeviceID if it contains '#'
        split_ids = set()
        for device_id in unique_ids:
            if "#" in device_id:
                split_id = device_id.split("#")[1]
                split_ids.add(split_id)
            else:
                split_ids.add(device_id)

        logging.info(f"Unique device IDs for device type '{device_type}': {split_ids}")
        return list(split_ids)

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
