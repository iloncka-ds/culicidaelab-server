from fastapi import APIRouter, Depends, Query, HTTPException, Path
from typing import Optional, List, Tuple
import lancedb
from backend.services import database, geo_service
from backend.schemas.geo_schemas import GeoJSONFeatureCollection

router = APIRouter()

VALID_LAYER_TYPES = ["distribution", "observations", "modeled", "breeding_sites"]


@router.get("/geo/{layer_type}", response_model=GeoJSONFeatureCollection)
async def get_geographic_layer(
    layer_type: str = Path(..., description=f"Type of geographic layer. Valid types: {', '.join(VALID_LAYER_TYPES)}"),
    db: lancedb.DBConnection = Depends(database.get_db),
    species: Optional[str] = Query(None, description="Comma-separated list of species scientific names to filter by"),
    bbox: Optional[str] = Query(None, description="Bounding box filter: min_lon,min_lat,max_lon,max_lat"),
    start_date: Optional[str] = Query(None, description="Start date for filtering (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for filtering (YYYY-MM-DD)"),
):
    """
    Retrieve geographic features for a specific layer, with optional filters.
    """
    if layer_type not in VALID_LAYER_TYPES:
        raise HTTPException(
            status_code=400, detail=f"Invalid layer type. Valid types are: {', '.join(VALID_LAYER_TYPES)}"
        )

    species_list: Optional[List[str]] = None
    if species:
        species_list = [s.strip() for s in species.split(",") if s.strip()]

    bbox_filter: Optional[Tuple[float, float, float, float]] = None
    if bbox:
        try:
            coords = [float(c.strip()) for c in bbox.split(",")]
            if len(coords) == 4:
                bbox_filter = (coords[0], coords[1], coords[2], coords[3])
            else:
                raise ValueError("Bounding box must have 4 coordinates.")
        except ValueError as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid bbox format: {e}. Use min_lon,min_lat,max_lon,max_lat"
            )

    if start_date and not geo_service.is_valid_date_str(start_date):
        raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
    if end_date and not geo_service.is_valid_date_str(end_date):
        raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")

    geojson_collection = geo_service.get_geo_layer(
        db=db,
        layer_type=layer_type,
        species_list=species_list,
        bbox_filter=bbox_filter,
        start_date_str=start_date,
        end_date_str=end_date,
    )
    return geojson_collection
