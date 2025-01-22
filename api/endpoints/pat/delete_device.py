from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import logging
from utils.api_utils import (
    get_dynamodb_table,
    get_device_info,
    delete_device_entries_from_devices_table,
    craft_delete_resposne,
    delete_device_entries_from_data_table,
)
from utils.air_utils import format_full_air_info
from constants.database import DATA_TABLE, DEVICE_TABLE

logger = logging.getLogger("pat_api")
router = APIRouter()


@router.delete(
    "/device",
    summary="Delete Device",
    response_description="Delete a device from the database",
)
async def delete_pat_device(
    device_name: str,
    data_table=Depends(lambda: get_dynamodb_table(DATA_TABLE)),
    device_table=Depends(lambda: get_dynamodb_table(DEVICE_TABLE)),
):
    if not data_table:
        logger.error("DynamoDB connection is unavailable.")
        raise HTTPException(status_code=500, detail="DynamoDB is unavailable")

    if not device_table:
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
        logging.info(f"device_info: {device_info}")

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        logger.error(f"Error fetching device info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    try:
        device_deleted_count = delete_device_entries_from_devices_table(
            device_table, device_id
        )
        logger.info(f"Deleted {device_deleted_count} items from device table")
    except HTTPException as e:
        logger.error(f"Error deleting device from device table: {e}")
        raise e

    try:
        data_deleted_count = delete_device_entries_from_data_table(
            data_table, device_id
        )
        logger.info(f"Deleted {data_deleted_count} items from data table")
    except HTTPException as e:
        logger.error(f"Error deleting device from data table: {e}")
        raise e

    return JSONResponse(
        status_code=200,
        content={
            "message": craft_delete_resposne(
                device_id, device_deleted_count, data_deleted_count
            )
        },
    )
