from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import lancedb
from backend.services import database, disease_service, species_service
from backend.schemas.diseases_schemas import DiseaseListResponse, Disease
from backend.schemas.species_schemas import SpeciesBase

router = APIRouter()


@router.get("/diseases", response_model=DiseaseListResponse)
async def get_disease_list_endpoint(
    db: lancedb.DBConnection = Depends(database.get_db),
    search: Optional[str] = Query(None, description="Search term for disease name or description"),
    limit: int = Query(50, ge=1, le=200, description="Number of results to return"),
    lang: str = Query("en", description="Language code for response (e.g., 'en', 'es')"),
):
    """
    Retrieve a list of vector-borne diseases, optionally filtered by a search term.
    """
    disease_list = disease_service.get_all_diseases(db, lang=lang, search=search, limit=limit)
    return DiseaseListResponse(count=len(disease_list), diseases=disease_list)


@router.get("/diseases/{disease_id}", response_model=Disease)
async def get_disease_detail_endpoint(
    disease_id: str,
    db: lancedb.DBConnection = Depends(database.get_db),
    lang: str = Query("en", description="Language code for response (e.g., 'en', 'es')"),
):
    """
    Retrieve detailed information for a specific disease by ID.
    """
    disease_detail = disease_service.get_disease_by_id(db, disease_id, lang)
    if not disease_detail:
        raise HTTPException(status_code=404, detail="Disease not found")
    return disease_detail


@router.get("/diseases/{disease_id}/vectors", response_model=List[SpeciesBase])
async def get_disease_vectors_endpoint(
    disease_id: str,
    db: lancedb.DBConnection = Depends(database.get_db),
    lang: str = Query("en", description="Language code for response (e.g., 'en', 'es')"),
):
    """
    Retrieve vector species associated with a specific disease.
    """
    # First, check if the disease exists
    disease_detail = disease_service.get_disease_by_id(db, disease_id, lang)
    if not disease_detail:
        raise HTTPException(status_code=404, detail="Disease not found")

    vector_species = species_service.get_vector_species(db, lang=lang, disease_id=disease_id)
    return vector_species
