from fastapi import APIRouter, Depends, Query
import lancedb
from backend.services import database
from backend.services import filter_service
from backend.schemas.filter_schemas import FilterOptions

router = APIRouter()


@router.get("/filter_options", response_model=FilterOptions)
async def get_filter_options_endpoint(
    db: lancedb.DBConnection = Depends(database.get_db),
    lang: str = Query("en", description="Language code for response (e.g., 'en', 'es')"),
):
    """
    Retrieve available filter options (species, regions, data sources) in the specified language.
    """
    return filter_service.get_filter_options(db, lang=lang)
