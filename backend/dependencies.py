from fastapi import Request, HTTPException
from typing import Dict
from backend.database_utils.lancedb_manager import get_lancedb_manager, LanceDBManager


async def get_db() -> LanceDBManager:
    return await get_lancedb_manager()


def get_region_cache(request: Request) -> Dict[str, Dict[str, str]]:
    """
    A dependency that retrieves the pre-loaded region translations
    cache from the application state.
    """
    cache = getattr(request.app.state, "REGION_TRANSLATIONS", None)
    if cache is None:
        # This is a critical failure, the app should not have started properly
        raise HTTPException(
            status_code=503,  # Service Unavailable
            detail="Region translations cache is not available. \
            The service may be starting up or has failed to initialize.",
        )
    return cache
