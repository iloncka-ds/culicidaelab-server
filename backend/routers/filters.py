
from typing import List, Dict
from fastapi import APIRouter, Depends, Query
import lancedb
from backend.services import database
from backend.services import filter_service
from backend.schemas.filter_schemas import FilterOptions
from dependencies import get_species_cache, get_region_cache, get_data_source_cache

router = APIRouter()


@router.get("/filter_options", response_model=FilterOptions)
async def get_filter_options_endpoint(
    lang: str = Query("en", description="Language code for response (e.g., 'en', 'es')"),
    species_names: List[str] = Depends(get_species_cache),
    region_translations: Dict = Depends(get_region_cache),
    data_source_translations: Dict = Depends(get_data_source_cache),
):
    """
    Retrieve available filter options (species, regions, data sources) in the specified language.
    """
    return filter_service.get_filter_options(lang=lang,
                            species_names=species_names,
                            region_translations=region_translations, data_source_translations=data_source_translations)
