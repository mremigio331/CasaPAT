from pydantic import BaseModel, Field
from utils.time_utils import get_current_utc_datetime
from typing import Optional


class AddDoorDeviceData(BaseModel):
    device_name: str = Field(..., example="test_device")
    timestamp: Optional[str] = Field(None, example=get_current_utc_datetime())
    door_status: str = Field(..., example="OPEN")
    battery: float = Field(
        ..., example=98.5, description="Battery level as a numeric value"
    )


class DoorDevice(BaseModel):
    device_name: str = Field(..., example="test_device")
