from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from datetime import datetime
import time

SERVICE_LOG_FILE = "/var/log/pat/service.log"


class ServiceLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        status_code = 500  # default if an unhandled exception escapes
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            request_id = getattr(request.state, "request_id", "-")
            client_ip = request.client.host if request.client else "-"
            path = request.url.path
            method = request.method
            duration_ms = int((time.perf_counter() - start) * 1000)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            msg = (
                f"-----------------\n"
                f"Timestamp={timestamp}\n"
                f"HTTP_Method={method}\n"
                f"Path={path}\n"
                f"Status={status_code}\n"
                f"IP={client_ip}\n"
                f"Request_id={request_id}\n"
                f"Latency={duration_ms}ms\n"
                f"-----------------\n"
            )

            print(msg)
            with open(SERVICE_LOG_FILE, "a") as f:
                f.write(msg + "\n")
