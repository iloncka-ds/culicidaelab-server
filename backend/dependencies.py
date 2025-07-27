from fastapi import Request, HTTPException
from typing import Dict, List
from backend.database_utils.lancedb_manager import get_lancedb_manager, LanceDBManager


async def get_db() -> LanceDBManager:
    return await get_lancedb_manager()


def get_cache(request: Request, cache_name: str):
    """Generic helper to get a cache from app state."""
    cache = getattr(request.app.state, cache_name, None)
    if cache is None:
        raise HTTPException(
            status_code=503, detail=f"{cache_name} is not available. Service may be initializing or failed."
        )
    return cache


def get_region_cache(request: Request) -> Dict[str, Dict[str, str]]:
    """Dependency for the regions translation cache."""
    return get_cache(request, "REGION_TRANSLATIONS")


def get_data_source_cache(request: Request) -> Dict[str, Dict[str, str]]:
    """Dependency for the data sources translation cache."""
    return get_cache(request, "DATASOURCE_TRANSLATIONS")


def get_species_cache(request: Request) -> List[str]:
    """Dependency for the species names list cache."""
    return get_cache(request, "SPECIES_NAMES")
