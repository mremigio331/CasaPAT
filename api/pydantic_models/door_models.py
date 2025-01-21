from pydantic import BaseModel, Field
from datetime import datetime

current_timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"


class AddDoorDeviceData(BaseModel):
    device_name: str = Field(..., example="test_device")
    timestamp: str = Field(..., example=current_timestamp)
    door_status: str = Field(..., example="OPEN")
    battery: float = Field(
        ..., example=98.5, description="Battery level as a numeric value"
    )


class DoorDevice(BaseModel):
    device_name: str = Field(..., example="test_device")
