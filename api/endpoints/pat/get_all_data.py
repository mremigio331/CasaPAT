from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import logging
from utils.api_utils import get_dynamodb_table, fetch_all_items
from constants.database import DATA_TABLE, DEVICE_TABLE

logger = logging.getLogger("pat_api")
router = APIRouter()


@router.get(
    "/database/all",
    summary="Get Entire Database",
    response_description="Retrieve all data from the devices and data tables.",
)
async def get_all_data(
    device_table=Depends(lambda: get_dynamodb_table(DEVICE_TABLE)),
    data_table=Depends(lambda: get_dynamodb_table(DATA_TABLE)),
):
    """Retrieve all entries from the PATDevices and PATData tables."""
    try:
        logger.info("Fetching entire database.")

        devices = fetch_all_items(device_table)
        data = fetch_all_items(data_table)

        response = {"devices": devices, "data": data}

        logger.info("Successfully fetched entire database.")
        return JSONResponse(content=response, status_code=200)

    except HTTPException as e:
        raise e  # Re-raise for proper response handling
    except Exception as e:
        logger.error(f"Unexpected error retrieving database: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error retrieving database"
        )
