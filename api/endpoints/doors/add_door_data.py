from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from decimal import Decimal
import logging
import json
from fastapi.responses import JSONResponse
from utils.api_utils import get_table

logger = logging.getLogger("pat_api")
router = APIRouter()
DOOR_OPTIONS = ["OPEN", "CLOSED"]


class DeviceData(BaseModel):
    DeviceID: str = Field(..., example="default_device")
    Timestamp: str = Field(..., example="2024-01-19T12:00:00Z")
    CurrentState: str = Field(..., example="OPEN")
    Battery: str = Field(
        ..., example="98.5", description="Battery level as a numeric string"
    )


@router.post(
    "/add_data/door_status",
    summary="Add Door Data",
    response_description="Add new data to DynamoDB",
)
async def add_data(
    DeviceID: str = Query(
        ..., example="device123", description="Unique identifier for the device"
    ),
    Timestamp: str = Query(
        ..., example="2024-01-19T12:00:00Z", description="ISO8601 timestamp"
    ),
    CurrentState: str = Query(
        ..., example="OPEN", description="Current door status (OPEN/CLOSED)"
    ),
    Battery: float = Query(
        ..., example=98.5, description="Battery level as a numeric value"
    ),
    table=Depends(get_table),
):
    """Add new door sensor data to DynamoDB."""
    logger.info("Called /doors/add_data endpoint.")

    if DeviceID == "default_device":
        logger.warning("Invalid DeviceID provided: default_device")
        raise HTTPException(
            status_code=400, detail="DeviceID cannot be 'default_device'."
        )

    if CurrentState not in DOOR_OPTIONS:
        logger.warning(f"Invalid CurrentState provided: {CurrentState}")
        raise HTTPException(
            status_code=400, detail="CurrentState must be 'OPEN' or 'CLOSED'."
        )

    try:
        battery_value = Decimal(str(Battery))
    except Exception:
        logger.warning(f"Invalid Battery value provided: {Battery}")
        raise HTTPException(
            status_code=400, detail="Battery value must be a valid number."
        )

    clean_up_data = {
        "DeviceID": f"DEVICE#{DeviceID}",
        "Timestamp": f"RECORD#{Timestamp}",
        "DeviceType": "DoorSensor",
        "DoorStatus": CurrentState,
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
