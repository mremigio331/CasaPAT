from fastapi import APIRouter, HTTPException, Depends
import logging
from fastapi.responses import JSONResponse
from utils.api_utils import get_dynamodb_table
from utils.door_utils import store_webhook
from constants.database import DEVICE_TABLE
from pydantic_models.door_models import RegisterWebhookRequest

logger = logging.getLogger("pat_api")
router = APIRouter()


@router.post(
    "/webhook/register",
    summary="Register Webhook",
    response_description="Register a webhook URL for door state notifications",
)
async def register_webhook(
    data: RegisterWebhookRequest,
    table=Depends(lambda: get_dynamodb_table(DEVICE_TABLE)),
):
    """Register a webhook URL to receive door state updates."""

    if not table:
        logger.error("DynamoDB connection is unavailable.")
        raise HTTPException(status_code=500, detail="DynamoDB is unavailable")

    if not data.webhook_url:
        logger.warning("No webhook_url provided")
        raise HTTPException(status_code=400, detail="webhook_url is required")

    try:
        logger.info(
            f"Registering webhook: {data.webhook_url} for device: {data.device_name}"
        )
        webhook_item = store_webhook(table, data.webhook_url, data.device_name)

        return JSONResponse(
            status_code=201,
            content={
                "message": "Webhook registered successfully",
                "webhook_id": webhook_item.get("WebhookID"),
                "webhook_url": webhook_item.get("WebhookURL"),
                "device_name": webhook_item.get("DeviceName"),
            },
        )
    except Exception as e:
        logger.error(f"Error registering webhook: {e}")
        raise HTTPException(status_code=500, detail="Error registering webhook")
