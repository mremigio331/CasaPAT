from fastapi import APIRouter, HTTPException, Depends
from decimal import Decimal
import logging
import json
from fastapi.responses import JSONResponse
from utils.api_utils import get_dynamodb_table, get_device_info, create_event_id
from constants.database import ISSUE_TABLE, DEVICE_TABLE
from pydantic_models.air_models import AirDeviceIssue
from utils.time_utils import get_current_utc_datetime

logger = logging.getLogger("pat_api")
router = APIRouter()


@router.post(
    "/add_issue",
    summary="Add Air Device Issue",
    response_description="Add air device issue/exception",
)
async def add_air_issue(
    data: AirDeviceIssue,
    issue_table=Depends(lambda: get_dynamodb_table(ISSUE_TABLE)),
    device_table=Depends(lambda: get_dynamodb_table(DEVICE_TABLE)),
):
    """Add new air device issue/exception to DynamoDB."""
    logger.info("Called /air/add_issue endpoint.")

    if data.timestamp:
        timestamp = data.timestamp
    else:
        timestamp = get_current_utc_datetime()

    try:
        if data.device_name:
            logger.info(f"Fetching device info for device: {data.device_name}")
            device_info = get_device_info(device_table, data.device_name)

            if not device_info:
                logger.warning(f"No device found with ID: {data.device_name}")
                raise HTTPException(
                    status_code=404,
                    detail=f"No device found with ID: {data.device_name}",
                )
            device_id = device_info.get("DeviceID")
        else:
            device_id = None

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        logger.error(f"Error fetching device info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    try:
        logger.info(f"Cleaning up issue data: {json.dumps(data.dict(), default=str)}")
        clean_up_data = {
            "DeviceID": device_id,
            "EventID": create_event_id(),
            "DeviceName": data.device_name,
            "Timestamp": timestamp,
            "Exception": data.exception,
            "ExceptionMessage": data.exception_message,
            "Type": "Issue",
        }

        # Remove None values
        clean_up_data = {k: v for k, v in clean_up_data.items() if v is not None}

    except Exception as e:
        logger.error(f"Error preparing issue data: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error while preparing data"
        )

    try:
        logger.info(
            f"Adding issue to DynamoDB: {json.dumps(clean_up_data, default=str)}"
        )
        issue_table.put_item(Item=clean_up_data)
        logger.info("Issue added successfully.")
        return JSONResponse(
            content={"message": "Issue added successfully"}, status_code=200
        )
    except Exception as e:
        logger.error(f"Error adding issue to DynamoDB: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error while adding issue"
        )
