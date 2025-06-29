from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import lancedb
from backend.services import database, disease_service, species_service
from backend.models import DiseaseListResponse, DiseaseDetail, SpeciesBase

router = APIRouter()


@router.get("/diseases", response_model=DiseaseListResponse)
async def get_disease_list_endpoint(
    db: lancedb.DBConnection = Depends(database.get_db),
    search: Optional[str] = Query(None, description="Search term for disease name or description"),
    limit: int = Query(50, ge=1, le=200, description="Number of results to return"),
):
    """
    Retrieve a list of vector-borne diseases, optionally filtered by a search term.
    """
    disease_list = disease_service.get_all_diseases(db, search=search, limit=limit)
    disease_dicts = [disease.model_dump() for disease in disease_list]
    return DiseaseListResponse(count=len(disease_dicts), diseases=disease_dicts)


@router.get("/diseases/{disease_id}", response_model=DiseaseDetail)
async def get_disease_detail_endpoint(disease_id: str, db: lancedb.DBConnection = Depends(database.get_db)):
    """
    Retrieve detailed information for a specific disease by ID.
    """
    disease_detail = disease_service.get_disease_by_id(db, disease_id)
    if not disease_detail:
        raise HTTPException(status_code=404, detail="Disease not found")
    return disease_detail


@router.get("/diseases/{disease_id}/vectors", response_model=List[SpeciesBase])
async def get_disease_vectors_endpoint(disease_id: str, db: lancedb.DBConnection = Depends(database.get_db)):
    """
    Retrieve vector species associated with a specific disease.
    """
    disease_detail = disease_service.get_disease_by_id(db, disease_id)
    if not disease_detail:
        raise HTTPException(status_code=404, detail="Disease not found")

    vector_species = species_service.get_vector_species(db, disease_id=disease_id)
    return vector_species
