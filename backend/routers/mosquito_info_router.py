# from fastapi import APIRouter, Depends, HTTPException, Query
# from typing import List, Optional

# from backend.database_utils.lancedb_manager import LanceDBManager
# from backend.dependencies import get_db
# from backend.services.species_service import SpeciesService
# from backend.schemas.species_schemas import Species, FilterOptionsResponse

# router = APIRouter()


# @router.get("/filter_options", response_model=FilterOptionsResponse)
# async def read_filter_options(db_manager: LanceDBManager = Depends(get_db)):
#     service = SpeciesService(db_manager)
#     options = await service.get_filter_options()
#     return options


# @router.get("/species", response_model=List[Species])
# async def read_all_species(
#     search: Optional[str] = None,
#     limit: int = Query(100, ge=1, le=1000),
#     offset: int = Query(0, ge=0),
#     db_manager: LanceDBManager = Depends(get_db),
# ):
#     service = SpeciesService(db_manager)
#     species_list = await service.get_all_species(search=search, limit=limit, offset=offset)
#     # Convert dicts to Pydantic models if necessary, Pydantic usually handles this
#     return [Species(**s) for s in species_list]


# @router.get("/species/{species_id}", response_model=Species)
# async def read_species_by_id(species_id: str, db_manager: LanceDBManager = Depends(get_db)):
#     service = SpeciesService(db_manager)
#     species = await service.get_species_by_id(species_id)
#     if not species:
#         raise HTTPException(status_code=404, detail="Species not found")
#     return Species(**species)
