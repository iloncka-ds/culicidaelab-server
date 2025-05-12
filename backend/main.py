from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.culicidaelab_api.config import settings
from backend.culicidaelab_api.routers import mosquito_info_router, geo_data_router
from backend.database.lancedb_manager import lancedb_manager  # Import the global instance

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

# CORS Middleware
# Adjust origins as needed for your frontend development and production
origins = [
    "http://localhost",  # Common for local dev
    "http://localhost:8503",  # Default Solara dev server port
    "http://localhost:8000",  # Default FastAPI dev server port (if serving frontend separately)
    # Add your production frontend URL here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Lifespan events for DB connection (optional for local LanceDB but good practice)
@app.on_event("startup")
async def startup_event():
    await lancedb_manager.connect()
    print("FastAPI application startup: LanceDB connection initialized.")


@app.on_event("shutdown")
async def shutdown_event():
    await lancedb_manager.close()  # Placeholder, as current LanceDB might not need explicit close
    print("FastAPI application shutdown: LanceDB connection (implicitly) closed.")


# Include routers
# Note: The frontend config uses /api/filter_options, /api/species, /api/geo/*
# We need to ensure our router prefixes match this.
# The frontend config.py has API_BASE_URL = "http://localhost:8000/api"
# So, these routers should be mounted at / (relative to API_BASE_URL).

# Example from frontend config:
# SPECIES_DISTRIBUTION_ENDPOINT = f"{API_BASE_URL}/geo/distribution"
# OBSERVATIONS_ENDPOINT = f"{API_BASE_URL}/geo/observations"
# MODELED_PROBABILITY_ENDPOINT = f"{API_BASE_URL}/geo/modeled_probability"
# BREEDING_SITES_ENDPOINT = f"{API_BASE_URL}/geo/breeding_sites"
# SPECIES_INFO_ENDPOINT = f"{API_BASE_URL}/species_info" # Should be /species for list, /species/{id} for detail
# FILTER_OPTIONS_ENDPOINT = f"{API_BASE_URL}/filter_options"

# Let's adjust router includes to match frontend expectations.
# The routers themselves define paths like "/filter_options", "/species", etc.
# If API_BASE_URL is "http://localhost:8000/api", and a router defines "/filter_options",
# the full path becomes "http://localhost:8000/api/filter_options".

app.include_router(mosquito_info_router.router, tags=["Mosquito Info"])
app.include_router(geo_data_router.router, prefix="/geo", tags=["Geographic Data"])  # This makes it /api/geo/*

# To match frontend exact paths:
# If mosquito_info_router handles /filter_options and /species, it's fine.
# If geo_data_router handles /distribution, /observations etc. directly under /geo prefix, it's fine.

# Check frontend config:
# SPECIES_DISTRIBUTION_ENDPOINT = f"{API_BASE_URL}/geo/distribution" - Matches
# SPECIES_INFO_ENDPOINT = f"{API_BASE_URL}/species_info" - Our router is /species and /species/{id}
#   We might need to rename the endpoint in frontend config or add an alias router.
#   For now, let's assume frontend will be updated to use /species.

# If you need an alias for `/species_info` to point to `/species` for the list:
# @app.get("/species_info", include_in_schema=False) # For list
# async def species_info_alias(
#     search: Optional[str] = None,
#     limit: int = Query(100, ge=1, le=1000),
#     offset: int = Query(0, ge=0),
#     db_manager: LanceDBManager = Depends(get_db)):
#     return await mosquito_info_router.read_all_species(search, limit, offset, db_manager)


if __name__ == "__main__":
    import uvicorn

    # Run with: uvicorn backend.culicidaelab_api.main:app --reload --port 8000
    # (Assuming you run this from the project root `culicidaelab-server/`)
    uvicorn.run(app, host="0.0.0.0", port=8000)
