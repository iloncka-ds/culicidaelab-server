from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.routers import filters, species, geo, diseases, prediction, observation
from backend.services.cache_service import (
    load_all_region_translations,
    load_all_datasource_translations,
    load_all_species_names,
)
from backend.services.database import get_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_conn = get_db()
    supported_languages = ["en", "ru"]
    # The loaded dictionary is stored in the app's state
    app.state.REGION_TRANSLATIONS = load_all_region_translations(db_conn, supported_languages)
    app.state.DATASOURCE_TRANSLATIONS = load_all_datasource_translations(db_conn, supported_languages)
    app.state.SPECIES_NAMES = load_all_species_names(db_conn)
    print("\n" + "=" * 20 + " DEBUGGING APP STATE " + "=" * 20)
    print(f"Has REGION_TRANSLATIONS: {hasattr(app.state, 'REGION_TRANSLATIONS')}")
    print(f"Has DATASOURCE_TRANSLATIONS: {hasattr(app.state, 'DATASOURCE_TRANSLATIONS')}")
    print(f"Has SPECIES_NAMES: {hasattr(app.state, 'SPECIES_NAMES')}")
    print("=" * 60 + "\n")


    print("Application startup: All caches initialized.")
    yield


app = FastAPI(title=settings.APP_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json", lifespan=lifespan)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

import os

# Get the directory where this file is located
backend_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(backend_dir, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

api_router_prefix = settings.API_V1_STR.replace("/api", "")

app.include_router(filters.router, prefix=settings.API_V1_STR, tags=["Filters"])
app.include_router(species.router, prefix=settings.API_V1_STR, tags=["Species"])
app.include_router(diseases.router, prefix=settings.API_V1_STR, tags=["Diseases"])
app.include_router(geo.router, prefix=settings.API_V1_STR, tags=["GeoData"])
app.include_router(prediction.router, prefix=settings.API_V1_STR, tags=["Prediction"])
app.include_router(observation.router, prefix=settings.API_V1_STR, tags=["Observation"])

@app.get(f"{api_router_prefix}/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.APP_NAME}"}


@app.get(f"{api_router_prefix}/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
