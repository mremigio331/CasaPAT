from fastapi import APIRouter, HTTPException, Depends
from decimal import Decimal
import logging
import json
from fastapi.responses import JSONResponse
from utils.api_utils import get_dynamodb_table, get_device_info
from constants.database import DATA_TABLE, DEVICE_TABLE
from pydantic_models.air_models import AddAirDeviceData

logger = logging.getLogger("pat_api")
router = APIRouter()


@router.post(
    "/add_data",
    summary="Add Air Data",
    response_description="Add updated air quality data",
)
async def add_air_data(
    data: AddAirDeviceData,
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

    try:
        logger.info(f"Cleaning up data: {json.dumps(data.dict(), default=str)}")
        clean_up_data = {
            "DeviceID": device_info.get("DeviceID"),
            "DeviceName": data.device_name,
            "Timestamp": data.timestamp,
            "PM25": Decimal(str(data.pm25)),
            "PM10": Decimal(str(data.pm10)),
        }

    except Exception as e:
        logger.error(f"Error converting floats to decimals: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error while converting floats"
        )

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
