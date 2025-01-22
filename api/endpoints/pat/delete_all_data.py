from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import logging
from utils.api_utils import get_dynamodb_table, batch_delete_table_items
from utils.air_utils import format_full_air_info
from constants.database import DATA_TABLE, DEVICE_TABLE

logger = logging.getLogger("pat_api")
router = APIRouter()


@router.delete(
    "/data/all",
    summary="Delete Device",
    response_description="Delete a device from the database",
)
async def delete_all_data(
    data_table=Depends(lambda: get_dynamodb_table(DATA_TABLE)),
    device_table=Depends(lambda: get_dynamodb_table(DEVICE_TABLE)),
):
    if not data_table:
        logger.error("DynamoDB connection is unavailable.")
        raise HTTPException(status_code=500, detail="DynamoDB is unavailable")

    if not device_table:
        logger.error("DynamoDB connection is unavailable.")
        raise HTTPException(status_code=500, detail="DynamoDB is unavailable")

    try:
        logger.info("Attempting to delete all data from the device table.")
        device_table_deleted_items_count = batch_delete_table_items(device_table)
        logger.info(
            f"Deleted {device_table_deleted_items_count} items from the device table."
        )
    except HTTPException as e:
        logger.error(f"Error deleting data from device table: {e}")
        raise e

    try:
        logger.info("Attempting to delete all data from the data table.")
        data_table_deleted_items_count = batch_delete_table_items(data_table)
        logger.info(
            f"Deleted {data_table_deleted_items_count} items from the data table."
        )
    except HTTPException as e:
        logger.error(f"Error deleting data from data table: {e}")
        raise e

    return JSONResponse(
        content={
            "message": "All data has been deleted from the database.",
            "delete_counts": {
                "device_table": device_table_deleted_items_count,
                "data_table": data_table_deleted_items_count,
            },
        },
        status_code=200,
    )
