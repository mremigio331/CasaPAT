from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from decimal import Decimal
import logging
import json
from fastapi.responses import JSONResponse
from utils.api_utils import get_dynamodb_table, unique_device_names, add_device
from constants.database import DEVICE_TABLE
from constants.door import DOOR_DEVICE_TYPE
from pydantic_models.door_models import DoorDevice

logger = logging.getLogger("pat_api")
router = APIRouter()


@router.post(
    "/register",
    summary="Add Device",
    response_description="Add a new door device",
)
async def register_door_device(
    data: DoorDevice, table=Depends(lambda: get_dynamodb_table((DEVICE_TABLE)))
):
    """Add new door sensor data to DynamoDB."""

    if data.device_name == "default_device":
        logger.warning("Invalid device_name provided: default_device")
        raise HTTPException(
            status_code=400, detail="device_name cannot be 'default_device'."
        )

    try:
        all_door_devices = unique_device_names(table, DOOR_DEVICE_TYPE)
        logger.info(f"Found all door devices: {all_door_devices}")

        if data.device_name in all_door_devices:
            logger.warning(f"Device already exists: {data.device_name}")
            return JSONResponse(
                status_code=409, content={"message": "Device already registered."}
            )

        logger.info(f"Adding new device: {data.device_name}")
        add_device(table, data.device_name, DOOR_DEVICE_TYPE)
        logger.info(f"Device {data.device_name} successfully added.")

        return JSONResponse(status_code=201, content={"message": "Device added."})

    except Exception as e:
        logger.error(
            f"Error processing registration for device {data.device_name}: {e}"
        )
        raise HTTPException(status_code=500, detail="Internal server error.")
