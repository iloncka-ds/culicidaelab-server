"""Main application module for CulicidaeLab API backend.

This module initializes and configures the FastAPI application, including:
- Application startup and shutdown lifecycle management
- CORS middleware configuration
- Static file serving setup
- API router registration
- Health check and root endpoints

The application serves as the main entry point for the CulicidaeLab API server,
providing endpoints for species identification, disease tracking, geographic
data, and observation management.

Example:
    >>> python -m backend.main
    # Starts the server on http://localhost:8000

    >>> # Or run with custom host/port
    >>> uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
"""

from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.logging_config import setup_logging, get_logger, log_with_context
from backend.routers import filters, species, geo, diseases, prediction, observation
from backend.services.cache_service import (
    load_all_region_translations,
    load_all_datasource_translations,
    load_all_species_names,
)
from backend.services.database import get_db

# Initialize logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages application startup and shutdown lifecycle.

    This context manager handles the initialization of database connections,
    cache loading, and other startup tasks when the FastAPI application starts,
    and cleanup when it shuts down.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: Control is yielded back to FastAPI after startup initialization.

    Example:
        >>> @asynccontextmanager
        >>> async def lifespan(app: FastAPI):
        >>>     # Initialize resources
        >>>     db = await init_database()
        >>>     app.state.db = db
        >>>     yield
        >>>     # Cleanup resources
        >>>     await db.close()
    """
    log_with_context(logger, "info", "Application startup initiated")

    try:
        db_conn = get_db()
        supported_languages = ["en", "ru"]

        # Load caches with logging
        log_with_context(logger, "info", "Loading region translations", languages=supported_languages)
        app.state.REGION_TRANSLATIONS = load_all_region_translations(db_conn, supported_languages)

        log_with_context(logger, "info", "Loading datasource translations", languages=supported_languages)
        app.state.DATASOURCE_TRANSLATIONS = load_all_datasource_translations(db_conn, supported_languages)

        log_with_context(logger, "info", "Loading species names")
        app.state.SPECIES_NAMES = load_all_species_names(db_conn)

        # Log cache initialization status
        cache_status = {
            "region_translations_loaded": hasattr(app.state, "REGION_TRANSLATIONS"),
            "datasource_translations_loaded": hasattr(app.state, "DATASOURCE_TRANSLATIONS"),
            "species_names_loaded": hasattr(app.state, "SPECIES_NAMES"),
            "region_count": len(app.state.REGION_TRANSLATIONS) if hasattr(app.state, "REGION_TRANSLATIONS") else 0,
            "datasource_count": len(app.state.DATASOURCE_TRANSLATIONS)
            if hasattr(app.state, "DATASOURCE_TRANSLATIONS")
            else 0,
            "species_count": len(app.state.SPECIES_NAMES) if hasattr(app.state, "SPECIES_NAMES") else 0,
        }

        log_with_context(logger, "info", "Application startup completed successfully", **cache_status)

    except Exception as e:
        log_with_context(logger, "error", "Application startup failed", error=str(e), error_type=type(e).__name__)
        raise

    yield

    log_with_context(logger, "info", "Application shutdown initiated")


app = FastAPI(title=settings.APP_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json", lifespan=lifespan)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Configure static file serving
import pathlib

# Get the directory where this file is located
backend_dir = pathlib.Path(__file__).parent.resolve()
static_dir = backend_dir / "static"

# Ensure static directory exists
static_dir.mkdir(parents=True, exist_ok=True)

# Create subdirectories if they don't exist
(static_dir / "images" / "species").mkdir(parents=True, exist_ok=True)
(static_dir / "images" / "diseases").mkdir(parents=True, exist_ok=True)
(static_dir / "images" / "predicted").mkdir(parents=True, exist_ok=True)

log_with_context(logger, "info", f"Static files directory: {static_dir}")

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

api_router_prefix = settings.API_V1_STR.replace("/api", "")

app.include_router(filters.router, prefix=settings.API_V1_STR, tags=["Filters"])
app.include_router(species.router, prefix=settings.API_V1_STR, tags=["Species"])
app.include_router(diseases.router, prefix=settings.API_V1_STR, tags=["Diseases"])
app.include_router(geo.router, prefix=settings.API_V1_STR, tags=["GeoData"])
app.include_router(prediction.router, prefix=settings.API_V1_STR, tags=["Prediction"])
app.include_router(observation.router, prefix=settings.API_V1_STR, tags=["Observation"])


@app.get(f"{settings.API_V1_STR}/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.APP_NAME}"}


@app.get(f"{settings.API_V1_STR}/static-test", tags=["Static"])
async def static_test():
    """Test endpoint to check static file configuration."""

    static_info = {
        "static_directory": str(static_dir),
        "static_exists": static_dir.exists(),
        "static_is_dir": static_dir.is_dir(),
        "contents": [],
    }

    if static_dir.exists():
        try:
            static_info["contents"] = [str(p.relative_to(static_dir)) for p in static_dir.rglob("*") if p.is_file()]
        except Exception as e:
            static_info["error"] = str(e)

    return static_info


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring and load balancing (root level).

    Returns:
        Dict containing health status and system information.
    """
    import time
    import psutil

    try:
        # Basic health check
        health_data = {
            "status": "ok",
            "timestamp": time.time(),
            "service": "culicidaelab-backend",
            "version": "1.0.0",
        }

        # Add system metrics in development mode
        if os.getenv("FASTAPI_ENV") == "development":
            health_data.update(
                {
                    "system": {
                        "cpu_percent": psutil.cpu_percent(),
                        "memory_percent": psutil.virtual_memory().percent,
                        "disk_percent": psutil.disk_usage("/").percent,
                    },
                },
            )

        # Check cache status
        cache_status = {
            "caches_loaded": all(
                [
                    hasattr(app.state, "REGION_TRANSLATIONS"),
                    hasattr(app.state, "DATASOURCE_TRANSLATIONS"),
                    hasattr(app.state, "SPECIES_NAMES"),
                ],
            ),
        }
        health_data.update(cache_status)

        log_with_context(logger, "debug", "Health check performed", **health_data)
        return health_data

    except Exception as e:
        log_with_context(logger, "error", "Health check failed", error=str(e), error_type=type(e).__name__)
        return {"status": "error", "message": str(e)}


@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
async def api_health_check():
    """Health check endpoint for API at /api/health.

    Returns:
        Dict containing health status and system information.
    """
    return await health_check()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
