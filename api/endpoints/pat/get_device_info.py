from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import logging
from utils.api_utils import get_dynamodb_table, get_device_info
from constants.database import DEVICE_TABLE

logger = logging.getLogger("pat_api")
router = APIRouter()


@router.get(
    "/info/device",
    summary="Get Device Info",
    response_description="Getting all info for a specific device",
)
async def get_door_device_info(
    device_name: str,
    table=Depends(lambda: get_dynamodb_table(DEVICE_TABLE)),
):
    if not table:
        logger.error("DynamoDB connection is unavailable.")
        raise HTTPException(status_code=500, detail="DynamoDB is unavailable")

    if device_name == "default_device":
        logger.warning("Invalid device_name provided: default_device")
        raise HTTPException(
            status_code=400, detail="device_name cannot be 'default_device'."
        )

    try:
        logger.info(f"Retrieving latest info for device: {device_name}")
        device_info = get_device_info(table, device_name)

        if not device_info:
            logger.info(f"No data found for device: {device_name}")
            raise HTTPException(
                status_code=404, detail=f"No data found for device {device_name}"
            )

        logger.info(f"Retrieved latest info for {device_name}: {device_info}")
        return JSONResponse(content={"device_info": device_info}, status_code=200)

    except HTTPException as e:
        raise e  # Re-raise expected HTTPExceptions

    except Exception as e:
        logger.error(f"Error retrieving latest info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
