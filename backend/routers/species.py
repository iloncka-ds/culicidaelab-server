"""Species router module for the Culicidae Lab Server.

This module provides FastAPI route handlers for mosquito species-related operations
in the Culicidae Lab application. It handles retrieval of species information,
including species lists, detailed species information, and disease vector species.

The router integrates with the species service layer to perform database queries
and return properly formatted responses according to the defined Pydantic schemas.

Routes:
    - GET /species: Retrieve a paginated list of mosquito species with optional search
    - GET /species/{species_id}: Retrieve detailed information for a specific species
    - GET /vector-species: Retrieve species that are known disease vectors

Example:
    The router is typically mounted in the main FastAPI application:

    ```python
    from fastapi import FastAPI
    from backend.routers.species import router as species_router

    app = FastAPI()
    app.include_router(species_router, prefix=\"/api/v1\")
    ```
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
import lancedb
from backend.services import database, species_service
from backend.schemas.species_schemas import SpeciesListResponse, SpeciesDetail, SpeciesBase
from backend.dependencies import get_region_cache


router = APIRouter()


@router.get("/species", response_model=SpeciesListResponse)
async def get_species_list_endpoint(
    request: Request,
    db: lancedb.DBConnection = Depends(database.get_db),
    search: str | None = Query(None, description="Search term for species name"),
    limit: int = Query(50, ge=1, le=200, description="Number of results to return"),
    lang: str = Query("en", description="Language code for response (e.g., 'en', 'es')"),
):
    """
    Retrieve a list of mosquito species, optionally filtered by a search term.

    This endpoint allows clients to fetch a paginated list of mosquito species
    from the database. The search functionality supports partial matching against
    scientific names and common names in English and Russian.

    Args:
        request: The FastAPI request object used for URL construction.
        db: LanceDB database connection for querying species data.
        search: Optional search term to filter species by name. Supports partial
            matching against scientific names and common names in multiple languages.
        limit: Maximum number of species to return (1-200). Defaults to 50.
        lang: Language code for response localization (e.g., 'en', 'es', 'ru').

    Returns:
        SpeciesListResponse: A response containing the count of species and the
            list of species matching the criteria.

    Raises:
        No exceptions are raised directly by this endpoint, but database errors
        may be logged and an empty result returned.

    Example:
        Get the first 25 mosquito species in English:

        ```python
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:8000/api/v1/species",
                params={"limit": 25, "lang": "en"}
            )
            species_data = response.json()
            print(f"Found {species_data['count']} species")
        ```

        Search for species containing "aedes":

        ```python
        response = await client.get(
            "http://localhost:8000/api/v1/species",
            params={"search": "aedes", "limit": 10, "lang": "en"}
        )
        ```
    """
    species_list = species_service.get_all_species(db, request, lang=lang, search=search, limit=limit)
    return SpeciesListResponse(count=len(species_list), species=species_list)


@router.get("/species/{species_id}", response_model=SpeciesDetail)
async def get_species_detail_endpoint(
    species_id: str,
    request: Request,
    region_cache: dict[str, dict[str, str]] = Depends(get_region_cache),
    db: lancedb.DBConnection = Depends(database.get_db),
    lang: str = Query("en", description="Language code for response (e.g., 'en', 'es')"),
):
    """
    Retrieve detailed information for a specific mosquito species by ID.

    This endpoint fetches comprehensive information about a single mosquito species
    including its scientific name, common names in multiple languages, vector status,
    habitat preferences, geographic regions, and associated diseases. The response
    includes translated content based on the requested language.

    Args:
        species_id: The unique identifier for the species (e.g., 'aedes-aegypti').
        request: The FastAPI request object used for URL construction.
        region_cache: Pre-loaded cache of region translations for localization.
        db: LanceDB database connection for querying species data.
        lang: Language code for response localization (e.g., 'en', 'es', 'ru').

    Returns:
        SpeciesDetail: Detailed information about the requested species including
            scientific name, common names, descriptions, characteristics, habitat
            preferences, geographic regions, and related diseases.

    Raises:
        HTTPException: If the species with the given ID is not found, returns a
            404 status code with detail message "Species not found".

    Example:
        Get detailed information for Aedes aegypti in English:

        ```python
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:8000/api/v1/species/aedes-aegypti",
                params={"lang": "en"}
            )
            if response.status_code == 200:
                species = response.json()
                print(f"Species: {species['scientific_name']}")
                print(f"Common name: {species['common_name']}")
                print(f"Vector status: {species['vector_status']}")
            else:
                print("Species not found")
        ```

        Get species information in Spanish:

        ```python
        response = await client.get(
            "http://localhost:8000/api/v1/species/anopheles-gambiae",
            params={"lang": "es"}
        )
        ```
    """
    species_detail = species_service.get_species_by_id(db, species_id, lang, region_cache, request)
    if not species_detail:
        raise HTTPException(status_code=404, detail="Species not found")
    return species_detail


@router.get("/vector-species", response_model=list[SpeciesBase])
async def get_vector_species_endpoint(
    request: Request,
    db: lancedb.DBConnection = Depends(database.get_db),
    disease_id: str | None = Query(None, description="Filter vectors by disease ID"),
    lang: str = Query("en", description="Language code for response (e.g., 'en', 'es')"),
):
    """
    Retrieve mosquito species that are disease vectors, optionally filtered by disease.

    This endpoint returns a list of mosquito species known to be vectors for various
    diseases. When a specific disease ID is provided, only species that are vectors
    for that particular disease are returned. Without a disease filter, all species
    marked as vectors (excluding 'None' and 'Unknown' status) are returned.

    Args:
        request: The FastAPI request object used for URL construction.
        db: LanceDB database connection for querying species data.
        disease_id: Optional specific disease ID to filter vectors. If provided,
            only species that are vectors for this disease will be returned.
        lang: Language code for response localization (e.g., 'en', 'es', 'ru').

    Returns:
        list[SpeciesBase]: A list of mosquito species that are disease vectors,
            filtered by the specified criteria.

    Raises:
        No exceptions are raised directly by this endpoint, but database errors
        may be logged and an empty result returned.

    Example:
        Get all mosquito species that are disease vectors in English:

        ```python
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:8000/api/v1/vector-species",
                params={"lang": "en"}
            )
            vector_species = response.json()
            print(f"Found {len(vector_species)} vector species")
            for species in vector_species:
                print(f"- {species['scientific_name']}: {species['vector_status']}")
        ```

        Get only species that are vectors for malaria:

        ```python
        # First, you'd need to know the disease ID for malaria
        response = await client.get(
            "http://localhost:8000/api/v1/vector-species",
            params={"disease_id": "malaria", "lang": "en"}
        )
        malaria_vectors = response.json()
        ```

        Get vector species in Russian:

        ```python
        response = await client.get(
            "http://localhost:8000/api/v1/vector-species",
            params={"lang": "ru"}
        )
        ```
    """
    vector_species = species_service.get_vector_species(db, request, lang=lang, disease_id=disease_id)
    return vector_species
