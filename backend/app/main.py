"""FastAPI application entrypoint with startup loading, CORS, and logging."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.loaders.csv_loader import get_dataset_metadata, load_crime_dataset
from app.routes.analytics import router as analytics_router
from app.routes.crimes import router as crimes_router
from app.routes.health import router as health_router
from app.routes.predictions import router as predictions_router
from app.routes.states import router as states_router


def configure_logging() -> None:
    """Set up application-wide logging once during startup."""

    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Load the static CSV dataset once before the app starts serving traffic."""

    configure_logging()
    logger = logging.getLogger(__name__)
    load_crime_dataset()
    logger.info("Dataset loaded successfully: %s", get_dataset_metadata())
    yield


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-ready backend for AI-powered crime analytics on Indian state-wise data.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(FileNotFoundError)
async def file_not_found_exception_handler(_: Request, exc: FileNotFoundError) -> JSONResponse:
    """Return a structured error when the dataset CSV cannot be found."""

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )


@app.exception_handler(ValueError)
async def value_error_exception_handler(_: Request, exc: ValueError) -> JSONResponse:
    """Return a structured error when dataset validation fails."""

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )


app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(states_router, prefix=settings.api_prefix)
app.include_router(crimes_router, prefix=settings.api_prefix)
app.include_router(analytics_router, prefix=settings.api_prefix)
app.include_router(predictions_router, prefix=settings.api_prefix)
