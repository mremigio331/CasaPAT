from pydantic import BaseModel, Field
from utils.time_utils import get_current_utc_datetime
from typing import Optional


class AddAirDeviceData(BaseModel):
    device_name: str = Field(..., example="test_device")
    timestamp: Optional[str] = Field(None, example=get_current_utc_datetime())
    pm25: float = Field(..., example=10.5, description="PM2.5 value as a numeric value")
    pm10: float = Field(..., example=20.5, description="PM10 value as a numeric value")


class AirDeviceIssue(BaseModel):
    device_name: Optional[str] = Field(None, example="test_device")
    timestamp: Optional[str] = Field(None, example=get_current_utc_datetime())
    exception: str = Field(..., example="SensorError")
    exception_message: str = Field(..., example="Failed to read sensor data")
