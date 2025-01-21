from fastapi import APIRouter, HTTPException, Depends
from decimal import Decimal
import logging
import json
from fastapi.responses import JSONResponse
from utils.api_utils import get_dynamodb_table
from constants.database import DATA_TABLE
from pydantic_models.door_models import AddDoorDeviceData

logger = logging.getLogger("pat_api")
router = APIRouter()
DOOR_OPTIONS = ["OPEN", "CLOSED"]


@router.post(
    "/add_data/door_status",
    summary="Add Door Data",
    response_description="Add new data to DynamoDB",
)
async def add_data(
    data: AddDoorDeviceData,
    table=Depends(lambda: get_dynamodb_table(DATA_TABLE)),
):
    """Add new door sensor data to DynamoDB."""
    logger.info("Called /doors/add_data endpoint.")

    if data.device_id == "default_device":
        logger.warning("Invalid device_id provided: default_device")
        raise HTTPException(
            status_code=400, detail="device_id cannot be 'default_device'."
        )

    if data.door_status not in DOOR_OPTIONS:
        logger.warning(f"Invalid door_status provided: {data.door_status}")
        raise HTTPException(
            status_code=400, detail="door_status must be 'OPEN' or 'CLOSED'."
        )

    try:
        battery_value = Decimal(str(data.battery))
    except Exception:
        logger.warning(f"Invalid battery value provided: {data.battery}")
        raise HTTPException(
            status_code=400, detail="battery value must be a valid number."
        )

    clean_up_data = {
        "DeviceID": f"DEVICE#{data.device_id}",
        "Timestamp": f"RECORD#{data.timestamp}",
        "DeviceType": "DoorSensor",
        "DoorStatus": data.door_status,
        "Battery": battery_value,
    }

    try:
        logger.info(
            f"Adding data to DynamoDB: {json.dumps(clean_up_data, default=str)}"
        )
        table.put_item(Item=clean_up_data)
        logger.info("Data added successfully.")
        return JSONResponse(
            content={"message": "Data added successfully"}, status_code=200
        )
    except Exception as e:
        logger.error(f"Error adding data to DynamoDB: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error while adding data"
        )
