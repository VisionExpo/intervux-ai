from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from backend.core.logging.logger import get_logger
from backend.core.exceptions.handlers import DomainError

logger = get_logger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """
    Registers global exception handlers for the application.
    Standardizes error responses for both API and internal domain errors.
    """
    
    @app.exception_handler(DomainError)
    async def domain_error_handler(_request: Request, exc: DomainError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "type": "domain_error"}
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        if isinstance(exc, HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail, "type": "api_error"}
            )
            
        logger.exception(
            "Unhandled server exception",
            extra={
                "extra_data": {
                    "method": request.method,
                    "path": request.url.path,
                }
            }
        )
        
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred.", "type": "internal_error"}
        )
