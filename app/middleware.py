import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.logger import logger

class CustomTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
       
        logger.info(f"Incoming request: {request.method} {request.url.path}")
       

        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        logger.info(
            f"Completed request: {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Duration: {process_time:.4f}s"
        )
        return response 