from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
import logging
from utils.api_utils import unique_device_names, get_dynamodb_table
from constants.database import DEVICE_TABLE
from constants.air import AIR_QUALITY_DEVICE_TYPE

logger = logging.getLogger("pat_api")
router = APIRouter()


@router.get(
    "/get_devices/air_devices",
    summary="Get All Air Quality Devices",
    response_description="Getting all air quality devices",
)
async def get_all_door_devices(
    table=Depends(lambda: get_dynamodb_table(DEVICE_TABLE)),
):
    if not table:
        logger.error("DynamoDB connection is unavailable.")
        return JSONResponse(
            content={"error": "DynamoDB is unavailable"}, status_code=500
        )

    try:
        air_sensors = unique_device_names(table, AIR_QUALITY_DEVICE_TYPE)
        logger.info(f"Retrieved unique device IDs: {air_sensors}")
        return JSONResponse(content={"devices": air_sensors}, status_code=200)
    except Exception as e:
        logger.error(f"Error retrieving devices: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
