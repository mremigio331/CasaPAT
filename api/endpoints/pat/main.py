from fastapi import APIRouter
from fastapi.responses import JSONResponse
import logging

router = APIRouter()


@router.get("/", summary="Home Endpoint", response_description="Welcome message")
async def home():
    """
    Home Endpoint

    Returns:
        A welcome message for the PAT API.
    """
    logging.info("Called home endpoint.")
    return JSONResponse(content={"message": "Welcome to PAT API"}, status_code=200)
