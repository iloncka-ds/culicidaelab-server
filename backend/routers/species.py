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
    Retrieve mosquito species that are disease vectors, optionally filtered by a specific disease.
    """
    vector_species = species_service.get_vector_species(db, request, lang=lang, disease_id=disease_id)
    return vector_species
