from endpoints.pat.main import router as home_router
from endpoints.doors import (
    add_door_data,
    get_all_door_devices,
    get_latest_door_info,
    get_all_door_info,
    register_door_device,
)


def get_all_routes(app):
    """Register all routers to the FastAPI app."""

    app.include_router(home_router, prefix="/pat", tags=["PAT"])

    # Door specific APIs
    app.include_router(add_door_data.router, prefix="/doors", tags=["Doors"])
    app.include_router(register_door_device.router, prefix="/doors", tags=["Doors"])
    app.include_router(get_all_door_devices.router, prefix="/doors", tags=["Doors"])
    app.include_router(get_latest_door_info.router, prefix="/doors", tags=["Doors"])
    app.include_router(get_all_door_info.router, prefix="/doors", tags=["Doors"])

    return app
