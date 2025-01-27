from fastapi import APIRouter, HTTPException, Depends
from decimal import Decimal
import logging
import json
from fastapi.responses import JSONResponse
from utils.api_utils import get_dynamodb_table, get_device_info, create_event_id
from constants.database import DATA_TABLE, DEVICE_TABLE
from constants.door import DOOR_OPTIONS
from pydantic_models.door_models import AddDoorDeviceData
from datetime import datetime, timezone

logger = logging.getLogger("pat_api")
router = APIRouter()


@router.post(
    "/add_data/door_status",
    summary="Add Door Data",
    response_description="Add new data to DynamoDB",
)
async def add_door_data(
    data: AddDoorDeviceData,
    data_table=Depends(lambda: get_dynamodb_table(DATA_TABLE)),
    device_table=Depends(lambda: get_dynamodb_table(DEVICE_TABLE)),
):
    """Add new door sensor data to DynamoDB."""
    logger.info("Called /doors/add_data endpoint.")

    if data.device_name == "default_device":
        logger.warning("Invalid device_name provided: default_device")
        raise HTTPException(
            status_code=400, detail="device_name cannot be 'default_device'."
        )

    if data.door_status not in DOOR_OPTIONS:
        logger.warning(f"Invalid door_status provided: {data.door_status}")
        raise HTTPException(
            status_code=400, detail="door_status must be 'OPEN' or 'CLOSED'."
        )

    try:
        logger.info(f"Fetching device info for device: {data.device_name}")
        device_info = get_device_info(device_table, data.device_name)

        if not device_info:
            logger.warning(f"No device found with ID: {data.device_name}")
            raise HTTPException(
                status_code=404, detail=f"No device found with ID: {data.device_name}"
            )

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        logger.error(f"Error fetching device info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    # Add timestamp if not provided
    if data.timestamp is None:
        data.timestamp = datetime.now(timezone.utc).isoformat()
        logger.info(f"No timestamp provided, using current UTC time: {data.timestamp}")

    try:
        battery_value = Decimal(str(data.battery))
    except Exception:
        logger.warning(f"Invalid battery value provided: {data.battery}")
        raise HTTPException(
            status_code=400, detail="battery value must be a valid number."
        )

    clean_up_data = {
        "DeviceID": device_info.get("DeviceID"),
        "EventID": create_event_id(),
        "DeviceName": data.device_name,
        "Timestamp": data.timestamp,
        "DeviceType": "DoorSensor",
        "DoorStatus": data.door_status,
        "Battery": battery_value,
    }

    try:
        logger.info(
            f"Adding data to DynamoDB: {json.dumps(clean_up_data, default=str)}"
        )
        data_table.put_item(Item=clean_up_data)
        logger.info("Data added successfully.")
        return JSONResponse(
            content={"message": "Data added successfully"}, status_code=200
        )
    except Exception as e:
        logger.error(f"Error adding data to DynamoDB: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error while adding data"
        )
