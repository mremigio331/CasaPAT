import subprocess
import threading
import time
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import logging
from fastapi import FastAPI

logger = logging.getLogger("pat_api")
router = APIRouter()

def _reboot_soon() -> None:
    time.sleep(10)
    subprocess.Popen(["/bin/systemctl", "reboot"])

@router.post("/restart")
def restart_pi():
    logger.info('Initiating restart')
    threading.Thread(target=_reboot_soon, daemon=True).start()
    return JSONResponse(
                status_code=202, content={"message": "Device already registered."}
            )
