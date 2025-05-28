from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.routers import filters, species, geo, diseases, prediction

app = FastAPI(title=settings.APP_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        # allow_origins=["*"], # Allow all for simple dev if needed, but restrict in prod
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
api_router_prefix = settings.API_V1_STR.replace("/api", "")  # Base prefix for routers

app.include_router(filters.router, prefix=settings.API_V1_STR, tags=["Filters"])
app.include_router(species.router, prefix=settings.API_V1_STR, tags=["Species"])
app.include_router(diseases.router, prefix=settings.API_V1_STR, tags=["Diseases"])
app.include_router(geo.router, prefix=settings.API_V1_STR, tags=["GeoData"])
app.include_router(prediction.router, prefix=settings.API_V1_STR, tags=["Prediction"])


@app.get(f"{api_router_prefix}/", tags=["Root"])  # Add base path endpoint
async def read_root():
    return {"message": f"Welcome to {settings.APP_NAME}"}


# Health check endpoint
@app.get(f"{api_router_prefix}/health", tags=["Health"])
async def health_check():
    # Can add DB connection check here later if needed
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    # Run with: uvicorn backend.main:app --reload --port 8000
    # (Assuming you run this from the project root `culicidaelab-server/`)
    uvicorn.run(app, host="0.0.0.0", port=8000)
