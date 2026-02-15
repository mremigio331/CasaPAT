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


class RegisterWebhookRequest(BaseModel):
    webhook_url: str = Field(..., example="http://homebridge.local:8080/webhook/doors")
    device_name: Optional[str] = Field(
        None,
        example="test_device",
        description="Optional: register for specific device only",
    )


class WebhookPayload(BaseModel):
    device_id: str
    device_name: str
    timestamp: str
    door_status: str
    battery: float
