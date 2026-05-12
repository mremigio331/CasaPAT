from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import logging
from utils.api_utils import get_dynamodb_table, get_device_info
from constants.database import DEVICE_TABLE
from pydantic_models.door_models import UpdateDeviceRequest

logger = logging.getLogger("pat_api")
router = APIRouter()


@router.put(
    "/data/device",
    summary="Update Device",
    response_description="Update a device's name or metadata",
)
async def update_device(
    data: UpdateDeviceRequest,
    device_table=Depends(lambda: get_dynamodb_table(DEVICE_TABLE)),
):
    if data.device_name == "default_device":
        raise HTTPException(status_code=400, detail="device_name cannot be 'default_device'.")

    try:
        device_info = get_device_info(device_table, data.device_name)
        if not device_info:
            raise HTTPException(status_code=404, detail=f"No device found: {data.device_name}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching device info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    device_id = device_info["DeviceID"]
    old_name = data.device_name
    new_name = data.new_device_name if data.new_device_name else old_name
    new_mfr = data.device_manufacturer if data.device_manufacturer else device_info.get("DeviceManufacturer")
    new_model = data.device_model if data.device_model else device_info.get("DeviceModel")

    try:
        if new_name != old_name:
            # DeviceName is part of the composite key — delete old item and recreate with new name
            device_table.delete_item(Key={"DeviceID": device_id, "DeviceName": old_name})
            new_item = {
                "DeviceID": device_id,
                "DeviceName": new_name,
                "DeviceType": device_info.get("DeviceType", ""),
                "DeviceManufacturer": new_mfr or "",
                "DeviceModel": new_model or "",
            }
            device_table.put_item(Item=new_item)
            logger.info(f"Renamed device '{old_name}' to '{new_name}'")
        else:
            update_parts = []
            expression_values = {}
            if new_mfr:
                update_parts.append("DeviceManufacturer = :mfr")
                expression_values[":mfr"] = new_mfr
            if new_model:
                update_parts.append("DeviceModel = :model")
                expression_values[":model"] = new_model

            if update_parts:
                device_table.update_item(
                    Key={"DeviceID": device_id, "DeviceName": old_name},
                    UpdateExpression="SET " + ", ".join(update_parts),
                    ExpressionAttributeValues=expression_values,
                )
                logger.info(f"Updated metadata for device '{old_name}'")

        return JSONResponse(status_code=200, content={"message": "Device updated successfully."})

    except Exception as e:
        logger.error(f"Error updating device '{data.device_name}': {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
