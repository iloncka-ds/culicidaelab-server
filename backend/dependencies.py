"""Dependencies module for CulicidaeLab API backend.

This module provides FastAPI dependency injection functions for accessing
shared resources and caches used throughout the application. Dependencies
are used to inject database connections and cached data into route handlers.

The module includes:
- Database connection dependency
- Cache access helpers for translation data
- Species data cache dependency

Example:
    >>> from backend.dependencies import get_db, get_region_cache
    >>>
    >>> @app.get("/regions")
    >>> async def get_regions(db = Depends(get_db), cache = Depends(get_region_cache)):
    >>>     # Use db and cache in your route handler
    >>>     pass
"""

from fastapi import Request, HTTPException
from backend.database_utils.lancedb_manager import get_lancedb_manager, LanceDBManager


async def get_db() -> LanceDBManager:
    """Provides database connection dependency for FastAPI routes.

    This dependency function creates and returns a LanceDB manager instance
    that can be injected into route handlers requiring database access.

    Returns:
        LanceDBManager: Configured LanceDB manager instance for database operations.

    Raises:
        Exception: If database connection cannot be established.

    Example:
        >>> @app.get("/observations")
        >>> async def get_observations(db: LanceDBManager = Depends(get_db)):
        >>>     observations = await db.get_observations()
        >>>     return observations
    """
    return await get_lancedb_manager()


def get_cache(request: Request, cache_name: str):
    """Generic helper to get a cache from app state.

    Retrieves a cached data structure from the FastAPI application's state.
    Used internally by specific cache dependency functions.

    Args:
        request (Request): The FastAPI request object containing app state.
        cache_name (str): Name of the cache to retrieve from app state.

    Returns:
        Any: The cached data structure if found.

    Raises:
        HTTPException: If the requested cache is not available in app state.

    Example:
        >>> cache = get_cache(request, "REGION_TRANSLATIONS")
        >>> regions = cache.get("en", {})
    """
    cache = getattr(request.app.state, cache_name, None)
    if cache is None:
        raise HTTPException(
            status_code=503,
            detail=f"{cache_name} is not available. Service may be initializing or failed.",
        )
    return cache


def get_region_cache(request: Request) -> dict[str, dict[str, str]]:
    """Dependency for the regions translation cache.

    Provides access to the cached region translations data, which maps
    region codes to translated names in multiple languages.

    Args:
        request (Request): The FastAPI request object containing app state.

    Returns:
        dict[str, dict[str, str]]: Dictionary mapping language codes to region
            translation dictionaries.

    Example:
        >>> @app.get("/regions/{language}")
        >>> async def get_regions_by_language(
        >>>     regions: dict = Depends(get_region_cache),
        >>>     language: str = "en"
        >>> ):
        >>>     return regions.get(language, {})
    """
    return get_cache(request, "REGION_TRANSLATIONS")


def get_data_source_cache(request: Request) -> dict[str, dict[str, str]]:
    """Dependency for the data sources translation cache.

    Provides access to the cached data source translations, which maps
    data source codes to translated names in multiple languages.

    Args:
        request (Request): The FastAPI request object containing app state.

    Returns:
        dict[str, dict[str, str]]: Dictionary mapping language codes to data
            source translation dictionaries.

    Example:
        >>> @app.get("/datasources/{language}")
        >>> async def get_data_sources_by_language(
        >>>     sources: dict = Depends(get_data_source_cache),
        >>>     language: str = "en"
        >>> ):
        >>>     return sources.get(language, {})
    """
    return get_cache(request, "DATASOURCE_TRANSLATIONS")


def get_species_cache(request: Request) -> list[str]:
    """Dependency for the species names list cache.

    Provides access to the cached list of all available species names
    for validation and autocomplete functionality.

    Args:
        request (Request): The FastAPI request object containing app state.

    Returns:
        list[str]: List of all available species names in the system.

    Example:
        >>> @app.get("/species")
        >>> async def get_all_species(
        >>>     species_list: list[str] = Depends(get_species_cache)
        >>> ):
        >>>     return {"species": species_list}
    """
    return get_cache(request, "SPECIES_NAMES")
