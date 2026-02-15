from endpoints.pat import (
    home,
    get_device_info,
    get_all_data,
    delete_device,
    delete_all_data,
)
from endpoints.doors import (
    add_door_data,
    get_all_door_devices,
    get_all_doors_current_state,
    get_full_door_device_info,
    door_get_latest_info,
    register_door_device,
    register_webhook,
)

from endpoints.air import (
    get_all_air_devices,
    get_latest_air_info,
    get_full_air_device_info,
    register_air_device,
    add_air_data,
    add_air_issue,
)


def get_all_routes(app):
    """Register all routers to the FastAPI app."""

    # General
    # Get
    app.include_router(home.router, prefix="/pat", tags=["General"])
    app.include_router(get_device_info.router, prefix="/pat", tags=["General"])
    app.include_router(get_all_data.router, prefix="/pat", tags=["General"])
    # Delete
    app.include_router(delete_all_data.router, prefix="/pat", tags=["General"])
    app.include_router(delete_device.router, prefix="/pat", tags=["General"])

    # Air Quality specific APIs
    # Get
    app.include_router(get_all_air_devices.router, prefix="/air", tags=["Air Quality"])
    app.include_router(get_device_info.router, prefix="/air", tags=["Air Quality"])
    app.include_router(
        get_full_air_device_info.router, prefix="/air", tags=["Air Quality"]
    )
    app.include_router(get_latest_air_info.router, prefix="/air", tags=["Air Quality"])
    # Post
    app.include_router(register_air_device.router, prefix="/air", tags=["Air Quality"])
    app.include_router(add_air_data.router, prefix="/air", tags=["Air Quality"])
    app.include_router(add_air_issue.router, prefix="/air", tags=["Air Quality"])

    # Door specific APIs
    # Get
    app.include_router(get_all_door_devices.router, prefix="/doors", tags=["Doors"])
    app.include_router(
        get_all_doors_current_state.router, prefix="/doors", tags=["Doors"]
    )
    app.include_router(
        get_full_door_device_info.router, prefix="/doors", tags=["Doors"]
    )
    app.include_router(get_device_info.router, prefix="/doors", tags=["Doors"])
    app.include_router(door_get_latest_info.router, prefix="/doors", tags=["Doors"])

    # Post
    app.include_router(add_door_data.router, prefix="/doors", tags=["Doors"])
    app.include_router(register_door_device.router, prefix="/doors", tags=["Doors"])
    app.include_router(register_webhook.router, prefix="/doors", tags=["Doors"])

    return app
