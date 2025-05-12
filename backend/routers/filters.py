from fastapi import APIRouter, Depends
import lancedb
from .. import database, services
from ..models import FilterOptions

router = APIRouter()


@router.get("/filter_options", response_model=FilterOptions)
async def get_filter_options_endpoint(db: lancedb.DBConnection = Depends(database.get_db)):
    """
    Retrieve available filter options (species, regions, data sources).
    """
    return services.filter_service.get_filter_options(db)
