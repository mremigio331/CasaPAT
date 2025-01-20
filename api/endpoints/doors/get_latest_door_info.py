from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import logging
from utils.api_utils import get_table
from utils.door_utils import get_latest_door_info
from pydantic import BaseModel, Field

logger = logging.getLogger("pat_api")
router = APIRouter()


class Device(BaseModel):
    device_id: str = Field(..., example="default_device")


@router.get(
    "/info/latest",
    summary="Get Latest Info",
    response_description="Getting latest info for a specific device",
)
async def get_latest_info(device_id: str, table=Depends(get_table)):
    if not table:
        logger.error("DynamoDB connection is unavailable.")
        raise HTTPException(status_code=500, detail="DynamoDB is unavailable")

    if device_id == "default_device":
        logger.warning("Invalid device_id provided: default_device")
        raise HTTPException(
            status_code=400, detail="device_id cannot be 'default_device'."
        )

    try:
        logger.info(f"Retrieving latest info for device: {device_id}")
        latest_info = get_latest_door_info(table, device_id)

        if not latest_info:
            logger.info(f"No data found for device: {device_id}")
            raise HTTPException(
                status_code=404, detail=f"No data found for device {device_id}"
            )

        logger.info(f"Retrieved latest info for {device_id}: {latest_info}")
        return JSONResponse(content={"latest_info": latest_info}, status_code=200)

    except HTTPException as e:
        raise e

    except Exception as e:
        logger.error(f"Error retrieving latest info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
