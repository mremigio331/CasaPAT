import logging
from utils.api_utils import get_latest_info
from fastapi import HTTPException

# Configure logger
logger = logging.getLogger("pat_api")


def get_latest_door_info(table, device_id: str):
    """Get the latest info for a specific door device."""
    logger.info(f"Fetching latest info for device_id: {device_id}")
    latest_info = get_latest_info(table, device_id)
    logger.info(f"Latest info: {latest_info}")

    if not latest_info:
        logger.warning(f"No latest info found for device_id: {device_id}")
        return None

    try:
        device_info = {
            "device_id": latest_info.get("DeviceID", "").split("#")[1],
            "timestamp": latest_info.get("Timestamp", "").split("#")[1],
            "current_state": latest_info.get("CurrentState"),
            "battery": float(latest_info.get("Battery", 0.0)),
        }
        logger.info(f"Latest info for device_id {device_id}: {device_info}")
        return device_info
    except (IndexError, ValueError, AttributeError) as e:
        logger.error(
            f"Error processing latest door info for device_id {device_id}: {e}"
        )
        raise ValueError(f"Error processing latest door info: {e}")
