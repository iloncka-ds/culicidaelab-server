"""Router module for filter-related API endpoints in CulicidaeLab.

This module provides FastAPI router endpoints for retrieving filter options
used throughout the CulicidaeLab application. It handles requests for species,
regions, and data source filtering options with multi-language support.

The module includes:
    - Filter options endpoint for retrieving available filter criteria
    - Integration with caching dependencies for performance
    - Localization support for multiple languages

Typical usage example:
    >>> from backend.routers.filters import router
    >>> app.include_router(router)

Attributes:
    router (APIRouter): FastAPI APIRouter instance containing filter-related endpoints.
"""

from fastapi import APIRouter, Depends, Query

from backend.services import filter_service
from backend.schemas.filter_schemas import FilterOptions
from backend.dependencies import get_species_cache, get_region_cache, get_data_source_cache

router: APIRouter = APIRouter()


@router.get("/filter_options", response_model=FilterOptions)
async def get_filter_options_endpoint(
    lang: str = Query("en", description="Language code for response (e.g., 'en', 'es')"),
    species_names: list[str] = Depends(get_species_cache),
    region_translations: dict = Depends(get_region_cache),
    data_source_translations: dict = Depends(get_data_source_cache),
):
    """Retrieves available filter options for species, regions, and data sources.

    This endpoint provides comprehensive filtering options that can be used across
    the CulicidaeLab application to filter disease data by various criteria.

    Args:
        lang: Language code for response localization (e.g., 'en' for English,
            'es' for Spanish). Defaults to 'en'.
        species_names: List of available mosquito species names for filtering.
        region_translations: Dictionary mapping region codes to translated names.
        data_source_translations: Dictionary mapping data source codes to translated names.

    Returns:
        FilterOptions: A structured response containing:
            - species: List of available mosquito species with their display names
            - regions: List of geographical regions with translated names
            - data_sources: List of data sources with translated names

    Example:
        >>> # Get filter options in English
        >>> response = await get_filter_options_endpoint("en", [...], {...}, {...})
        >>> print(response.species)  # List of species options
        >>> print(response.regions)  # List of region options

        >>> # Get filter options in Spanish
        >>> response = await get_filter_options_endpoint("es", [...], {...}, {...})
        >>> print(response.species)  # Lista de opciones de especies
    """
    return filter_service.get_filter_options(
        lang=lang,
        species_names=species_names,
        region_translations=region_translations,
        data_source_translations=data_source_translations,
    )
