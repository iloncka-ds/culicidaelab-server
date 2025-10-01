"""
Disease-related API endpoints for the CulicidaeLab server.

This module provides FastAPI router endpoints for retrieving information about vector-borne
diseases and their associated arthropod vectors. The endpoints support multiple languages
and provide both list and detail views of diseases.

The module includes the following endpoints:
- GET /diseases: Retrieve a paginated list of diseases with optional search filtering
- GET /diseases/{disease_id}: Retrieve detailed information for a specific disease
- GET /diseases/{disease_id}/vectors: Retrieve vector species associated with a disease

All endpoints support internationalization and return data in the requested language.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
import lancedb
from backend.services import database, disease_service, species_service
from backend.schemas.diseases_schemas import DiseaseListResponse, Disease
from backend.schemas.species_schemas import SpeciesBase


router = APIRouter()


@router.get("/diseases", response_model=DiseaseListResponse)
async def get_disease_list_endpoint(
    request: Request,
    db: lancedb.DBConnection = Depends(database.get_db),
    search: str | None = Query(None, description="Search term for disease name or description"),
    limit: int = Query(50, ge=1, le=200, description="Number of results to return"),
    lang: str = Query("en", description="Language code for response (e.g., 'en', 'es')"),
):
    """
    Retrieve a list of vector-borne diseases, optionally filtered by a search term.

    This endpoint provides a paginated list of diseases that can be filtered by name or description.
    Results are localized based on the requested language and support various query parameters
    for flexible disease discovery and analysis.

    Args:
        request (Request): The FastAPI request object containing client information and headers.
        db (lancedb.DBConnection): Database connection dependency for querying disease data from
            the LanceDB vector database.
        search (str | None): Optional search term to filter diseases by name or description.
            Performs case-insensitive substring matching. If None, returns all diseases.
            Examples: "malaria", "fever", "mosquito".
        limit (int): Maximum number of diseases to return per page (1-200). Defaults to 50.
            Use this parameter for pagination control when dealing with large result sets.
        lang (str): Language code for response localization and internationalization.
            Supported languages: 'en' (English), 'es' (Spanish), 'fr' (French), 'pt' (Portuguese).
            Defaults to 'en' for English responses.

    Returns:
        DiseaseListResponse: A structured response containing:
            - count (int): Total number of diseases matching the search criteria
            - diseases (list[Disease]): List of disease objects with basic information

    Example:
        Basic disease list retrieval:
        GET /diseases?limit=10&lang=en

        Search for specific diseases:
        GET /diseases?search=malaria&limit=5&lang=en

        Multilingual support:
        GET /diseases?search=fiebre&lang=en

        Response format:
        {
            "count": 2,
            "diseases": [
                {
                    "id": "malaria",
                    "name": "Malaria",
                    "description": "A life-threatening disease caused by Plasmodium parasites...",
                    "vectors": ["Anopheles mosquito"]
                },
                {
                    "id": "dengue",
                    "name": "Dengue Fever",
                    "description": "A mosquito-borne viral infection causing flu-like illness...",
                    "vectors": ["Aedes aegypti", "Aedes albopictus"]
                }
            ]
        }
    """
    disease_list = disease_service.get_all_diseases(db, request, lang=lang, search=search, limit=limit)
    return DiseaseListResponse(count=len(disease_list), diseases=disease_list)


@router.get("/diseases/{disease_id}", response_model=Disease)
async def get_disease_detail_endpoint(
    disease_id: str,
    request: Request,
    db: lancedb.DBConnection = Depends(database.get_db),
    lang: str = Query("en", description="Language code for response (e.g., 'en', 'es')"),
):
    """
    Retrieve detailed information for a specific disease by ID.

    This endpoint provides comprehensive information about a specific vector-borne disease,
    including its description, associated vectors, symptoms, and other relevant details.
    Results are localized based on the requested language.

    Args:
        disease_id (str): Unique identifier for the disease (e.g., 'malaria', 'dengue').
            This is typically the disease name in lowercase with hyphens.
        request (Request): The FastAPI request object containing client information.
        db (lancedb.DBConnection): Database connection dependency for querying disease data.
        lang (str): Language code for response localization (e.g., 'en', 'es', 'fr').
            Defaults to 'en' for English.

    Returns:
        Disease: A detailed disease object containing all available information about
            the specified disease, or None if the disease is not found.

    Raises:
        HTTPException: If the disease with the specified ID is not found (404 status code).

    Example:
        GET /diseases/malaria?lang=en
        Response:
        {
            "id": "malaria",
            "name": "Malaria",
            "description": "A life-threatening disease caused by Plasmodium parasites...",
            "symptoms": ["Fever", "Chills", "Headache"],
            "vectors": ["Anopheles gambiae", "Anopheles funestus"],
            "regions": ["Sub-Saharan Africa", "Southeast Asia"],
            "transmission": "Bite of infected female Anopheles mosquitoes"
        }
    """
    disease_detail = disease_service.get_disease_by_id(db, disease_id, lang, request)
    if not disease_detail:
        raise HTTPException(status_code=404, detail="Disease not found")
    return disease_detail


@router.get("/diseases/{disease_id}/vectors", response_model=list[SpeciesBase])
async def get_disease_vectors_endpoint(
    disease_id: str,
    request: Request,
    db: lancedb.DBConnection = Depends(database.get_db),
    lang: str = Query("en", description="Language code for response (e.g., 'en', 'es')"),
):
    """
    Retrieve vector species associated with a specific disease.

    This endpoint returns a list of arthropod vectors (primarily mosquitoes, ticks, and flies)
    that are known to transmit the specified disease. This information is crucial for
    understanding disease transmission patterns and vector control strategies.

    Args:
        disease_id (str): Unique identifier for the disease (e.g., 'malaria', 'lyme-disease').
            This is typically the disease name in lowercase with hyphens.
        request (Request): The FastAPI request object containing client information.
        db (lancedb.DBConnection): Database connection dependency for querying species data.
        lang (str): Language code for response localization (e.g., 'en', 'es', 'fr').
            Defaults to 'en' for English.

    Returns:
        list[SpeciesBase]: A list of species objects that serve as vectors for the specified
            disease. Each species includes taxonomic information and habitat details.

    Raises:
        HTTPException: If the disease with the specified ID is not found (404 status code).

    Example:
        GET /diseases/malaria/vectors?lang=en
        Response:
        [
            {
                "id": "anopheles-gambiae",
                "scientific_name": "Anopheles gambiae",
                "common_name": "African malaria mosquito",
                "genus": "Anopheles",
                "family": "Culicidae",
                "habitat": "Tropical and subtropical regions",
                "distribution": "Sub-Saharan Africa"
            },
            {
                "id": "anopheles-funestus",
                "scientific_name": "Anopheles funestus",
                "common_name": "Common malaria mosquito",
                "genus": "Anopheles",
                "family": "Culicidae",
                "habitat": "Rural and peri-urban areas",
                "distribution": "Africa south of the Sahara"
            }
        ]
    """
    disease_detail = disease_service.get_disease_by_id(db, disease_id, lang, request)
    if not disease_detail:
        raise HTTPException(status_code=404, detail="Disease not found")

    vector_species = species_service.get_vector_species(db, request, lang=lang, disease_id=disease_id)
    return vector_species
