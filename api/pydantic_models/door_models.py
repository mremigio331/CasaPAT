from pydantic import BaseModel, Field


class AddDoorDeviceData(BaseModel):
    device_name: str = Field(..., example="test_device")
    timestamp: str = Field(..., example="2024-01-19T12:00:00Z")
    door_status: str = Field(..., example="OPEN")
    battery: float = Field(
        ..., example=98.5, description="Battery level as a numeric value"
    )


class DoorDevice(BaseModel):
    device_name: str = Field(..., example="test_device")
