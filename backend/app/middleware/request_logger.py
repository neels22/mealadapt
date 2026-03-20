"""
Request logging middleware for observability.
Logs method, path, status code, and response time for every request.
"""
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("mealadapt.requests")


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        method = request.method
        path = request.url.path

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.error(
                "%s %s 500 %.1fms (unhandled exception)",
                method, path, duration_ms
            )
            raise

        duration_ms = (time.perf_counter() - start) * 1000
        status = response.status_code

        if status >= 500:
            logger.error("%s %s %d %.1fms", method, path, status, duration_ms)
        elif status >= 400:
            logger.warning("%s %s %d %.1fms", method, path, status, duration_ms)
        else:
            logger.info("%s %s %d %.1fms", method, path, status, duration_ms)

        return response
