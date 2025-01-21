from endpoints.pat.main import router as home_router
from endpoints.doors import (
    add_door_data,
    get_all_door_devices,
    get_latest_door_info,
    get_all_door_info,
    get_door_device_info,
    register_door_device,
)

from endpoints.air import get_all_air_devices, register_air_device, add_air_data


def get_all_routes(app):
    """Register all routers to the FastAPI app."""

    app.include_router(home_router, prefix="/pat", tags=["PAT"])

    # Air Quality specific APIs
    # Get
    app.include_router(get_all_air_devices.router, prefix="/air", tags=["Air Quality"])
    # Post
    app.include_router(register_air_device.router, prefix="/air", tags=["Air Quality"])
    app.include_router(add_air_data.router, prefix="/air", tags=["Air Quality"])

    # Door specific APIs
    # Get
    app.include_router(get_all_door_devices.router, prefix="/doors", tags=["Doors"])
    app.include_router(get_all_door_info.router, prefix="/doors", tags=["Doors"])
    app.include_router(get_door_device_info.router, prefix="/doors", tags=["Doors"])
    app.include_router(get_latest_door_info.router, prefix="/doors", tags=["Doors"])

    # Post
    app.include_router(add_door_data.router, prefix="/doors", tags=["Doors"])
    app.include_router(register_door_device.router, prefix="/doors", tags=["Doors"])

    return app
