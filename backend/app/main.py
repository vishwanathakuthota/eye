from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.responses import error_response

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs" if settings.app_env == "development" else None,
        redoc_url="/redoc" if settings.app_env == "development" else None,
        openapi_url="/openapi.json" if settings.app_env == "development" else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api_cors_origins,
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        logger.info("request_validation_failed", extra={"source": "api"})
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(
                code="VALIDATION_ERROR",
                message="The request is invalid.",
                details={"errors": exc.errors()},
            ),
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:
        logger.exception(
            "unhandled_api_error",
            extra={"source": "api", "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR},
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(
                code="INTERNAL_ERROR",
                message="An unexpected server error occurred.",
            ),
        )

    return app


app = create_app()
