from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import logging
from utils.api_utils import get_dynamodb_table, get_device_info
from utils.door_utils import get_latest_door_info
from constants.database import DATA_TABLE, DEVICE_TABLE
from constants.door import DOOR_DEVICE_TYPE

logger = logging.getLogger("pat_api")
router = APIRouter()


@router.get(
    "/info/latest",
    summary="Get Latest Info",
    response_description="Getting latest info for a specific device",
)
async def door_get_latest_info(
    device_name: str,
    data_table=Depends(lambda: get_dynamodb_table(DATA_TABLE)),
    device_table=Depends(lambda: get_dynamodb_table(DEVICE_TABLE)),
):
    if not data_table:
        logger.error("DynamoDB connection is unavailable.")
        raise HTTPException(status_code=500, detail="DynamoDB is unavailable")

    if device_name == "default_device":
        logger.warning("Invalid device_id provided: default_device")
        raise HTTPException(
            status_code=400, detail="device_id cannot be 'default_device'."
        )

    try:
        logger.info(f"Fetching device info for device: {device_name}")
        device_info = get_device_info(device_table, device_name)

        if not device_info:
            logger.warning(f"No device found with ID: {device_name}")
            raise HTTPException(
                status_code=404, detail=f"No device found with ID: {device_name}"
            )
        device_id = device_info.get("DeviceID")

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        logger.error(f"Error fetching device info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    if device_info.get("DeviceType") != DOOR_DEVICE_TYPE:
        logger.warning(f"Device {device_name} is not a Door device.")
        raise HTTPException(
            status_code=400, detail=f"Device {device_name} is not a Door device."
        )

    try:
        logger.info(f"Retrieving latest info for device: {device_name}")
        latest_info = get_latest_door_info(data_table, device_id)

        if not latest_info:
            logger.info(f"No data found for device: {device_name}")
            raise HTTPException(
                status_code=404, detail=f"No data found for device {device_name}"
            )

        logger.info(f"Retrieved latest info for {device_name}: {latest_info}")
        return JSONResponse(content={"latest_info": latest_info}, status_code=200)

    except HTTPException as e:
        raise e

    except Exception as e:
        logger.error(f"Error retrieving latest info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
