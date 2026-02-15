from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import logging
from utils.api_utils import get_dynamodb_table, unique_device_names, get_device_info
from utils.door_utils import get_latest_door_info
from constants.database import DATA_TABLE, DEVICE_TABLE
from constants.door import DOOR_DEVICE_TYPE

logger = logging.getLogger("pat_api")
router = APIRouter()


@router.get(
    "/current_state",
    summary="Get All Doors Current State",
    response_description="Getting current state for all door devices",
)
async def get_all_doors_current_state(
    data_table=Depends(lambda: get_dynamodb_table(DATA_TABLE)),
    device_table=Depends(lambda: get_dynamodb_table(DEVICE_TABLE)),
):
    if not data_table or not device_table:
        logger.error("DynamoDB connection is unavailable.")
        raise HTTPException(status_code=500, detail="DynamoDB is unavailable")

    try:
        # Get all door device names
        logger.info("Fetching all door devices")
        door_device_names = unique_device_names(device_table, DOOR_DEVICE_TYPE)

        if not door_device_names:
            logger.info("No door devices found")
            return JSONResponse(content={"devices": []}, status_code=200)

        # Get latest state for each door device
        all_door_states = []
        for device_name in door_device_names:
            try:
                logger.debug(f"Fetching device info for: {device_name}")
                device_info = get_device_info(device_table, device_name)

                if not device_info:
                    logger.warning(f"No device info found for device: {device_name}")
                    all_door_states.append(
                        {
                            "device_id": device_name,
                            "event_id": None,
                            "timestamp": None,
                            "door_status": None,
                            "battery": None,
                        }
                    )
                    continue

                device_id = device_info.get("DeviceID")
                logger.debug(f"Fetching latest state for device_id: {device_id}")
                door_state = get_latest_door_info(data_table, device_id)

                if door_state:
                    all_door_states.append(door_state)
                else:
                    logger.warning(f"No state found for device: {device_name}")
                    all_door_states.append(
                        {
                            "device_id": device_name,
                            "event_id": None,
                            "timestamp": None,
                            "door_status": None,
                            "battery": None,
                        }
                    )
            except Exception as e:
                logger.error(f"Error fetching state for device {device_name}: {e}")
                all_door_states.append(
                    {
                        "device_id": device_name,
                        "event_id": None,
                        "timestamp": None,
                        "door_status": None,
                        "battery": None,
                    }
                )

        logger.info(f"Retrieved current state for {len(all_door_states)} door devices")
        return JSONResponse(content={"devices": all_door_states}, status_code=200)

    except Exception as e:
        logger.error(f"Error retrieving all doors current state: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
