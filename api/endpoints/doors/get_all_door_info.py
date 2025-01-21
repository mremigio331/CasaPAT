from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import logging
from utils.api_utils import get_dynamodb_table
from utils.door_utils import format_all_door_info
from constants.database import DATA_TABLE

logger = logging.getLogger("pat_api")
router = APIRouter()


@router.get(
    "/info/all",
    summary="Get All Info",
    response_description="Getting all info for a specific device",
)
async def get_all_door_info(
    device_id: str,
    table=Depends(lambda: get_dynamodb_table(DATA_TABLE)),
):
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
        all_info = format_all_door_info(table, device_id)

        if not all_info:
            logger.info(f"No data found for device: {device_id}")
            raise HTTPException(
                status_code=404, detail=f"No data found for device {device_id}"
            )

        logger.info(f"Retrieved latest info for {device_id}: {all_info}")
        return JSONResponse(content={"latest_info": all_info}, status_code=200)

    except HTTPException as e:
        raise e  # Re-raise expected HTTPExceptions

    except Exception as e:
        logger.error(f"Error retrieving latest info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
