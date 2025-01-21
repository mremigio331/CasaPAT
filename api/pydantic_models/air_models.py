from pydantic import BaseModel, Field
from datetime import datetime

current_timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"


class AddAirDeviceData(BaseModel):
    device_name: str = Field(..., example="test_device")
    timestamp: str = Field(..., example=current_timestamp)
    pm25: float = Field(..., example=10.5, description="PM2.5 value as a numeric value")
    pm10: float = Field(..., example=20.5, description="PM10 value as a numeric value")
