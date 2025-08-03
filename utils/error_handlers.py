# utils/error_handlers.py

from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_exception_handlers(app: FastAPI):
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception for request {request.url}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "An internal server error occurred.", "detail": str(exc)},
        )