from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from decimal import Decimal
import logging
import json
from fastapi.responses import JSONResponse
from utils.api_utils import get_dynamodb_table
from constants.database import DEVICE_TABLE

logger = logging.getLogger("pat_api")
router = APIRouter()
DOOR_OPTIONS = ["OPEN", "CLOSED"]


class Device(BaseModel):
    device_id: str = Field(..., example="test_device")
    device_type: str = Field(..., example="DoorSensor")


@router.post(
    "/register",
    summary="Add Device",
    response_description="Add a new door device",
)
async def add_data(
    data: Device,
    table=Depends(get_dynamodb_table(DEVICE_TABLE)),
):
    """Add new door sensor data to DynamoDB."""
    logger.info("Called /doors/register endpoint.")

    if data.device_id == "default_device":
        logger.warning("Invalid device_id provided: default_device")
        raise HTTPException(
            status_code=400, detail="device_id cannot be 'default_device'."
        )

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
