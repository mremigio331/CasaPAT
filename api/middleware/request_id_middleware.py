import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from utils.request_context import request_id_ctx

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())

        # store on request.state (you already wanted this)
        request.state.request_id = request_id

        # store in contextvar for logging
        token = request_id_ctx.set(request_id)
        try:
            response = await call_next(request)
            response.headers["x-request-id"] = request_id
            return response
        finally:
            request_id_ctx.reset(token)