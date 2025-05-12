from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional, Dict, Any

from backend.database.lancedb_manager import LanceDBManager
from backend.culicidaelab_api.dependencies import get_db
from backend.culicidaelab_api.services.geo_service import GeoService
from backend.culicidaelab_api.schemas.geo_schemas import GeoJSONFeatureCollection  # Using this as response

router = APIRouter()


async def get_layer_data_for_type(
    layer_type: str,
    species_query: Optional[str] = Query(None, description="Comma-separated list of species scientific names"),
    bbox: Optional[str] = Query(None, description="Bounding box: min_lon,min_lat,max_lon,max_lat"),
    # date_range: Optional[str] = Query(None, description="Date range: YYYY-MM-DD,YYYY-MM-DD"), # Example for future
    db_manager: LanceDBManager = Depends(get_db),
) -> GeoJSONFeatureCollection:
    service = GeoService(db_manager)
    species_list = species_query.split(",") if species_query else None

    # Add date_range to service call if implemented
    data = await service.get_map_layer_data(
        layer_type,
        species=species_list,
        bbox_filter=bbox,
        # date_range_filter=date_range # Example for future
    )
    if data is None:  # Service indicates layer type itself not found or error
        raise HTTPException(status_code=404, detail=f"Layer data for type '{layer_type}' not found.")

    return GeoJSONFeatureCollection(**data)


@router.get("/distribution", response_model=GeoJSONFeatureCollection)
async def get_distribution_data(
    species: Optional[str] = Query(
        None, alias="species", description="Comma-separated list of species scientific names"
    ),
    bbox: Optional[str] = Query(None, description="Bounding box: min_lon,min_lat,max_lon,max_lat"),
    db: LanceDBManager = Depends(get_db),
):
    return await get_layer_data_for_type("distribution", species_query=species, bbox=bbox, db_manager=db)


@router.get("/observations", response_model=GeoJSONFeatureCollection)
async def get_observations_data(
    species: Optional[str] = Query(
        None, alias="species", description="Comma-separated list of species scientific names"
    ),
    bbox: Optional[str] = Query(None, description="Bounding box: min_lon,min_lat,max_lon,max_lat"),
    db: LanceDBManager = Depends(get_db),
):
    return await get_layer_data_for_type("observations", species_query=species, bbox=bbox, db_manager=db)


@router.get("/modeled_probability", response_model=GeoJSONFeatureCollection)  # Endpoint name matches frontend config
async def get_modeled_probability_data(  # Function name updated for consistency
    species: Optional[str] = Query(
        None, alias="species", description="Comma-separated list of species scientific names"
    ),
    bbox: Optional[str] = Query(None, description="Bounding box: min_lon,min_lat,max_lon,max_lat"),
    db: LanceDBManager = Depends(get_db),
):
    return await get_layer_data_for_type(
        "modeled", species_query=species, bbox=bbox, db_manager=db
    )  # 'modeled' is the type


@router.get("/breeding_sites", response_model=GeoJSONFeatureCollection)
async def get_breeding_sites_data(
    species: Optional[str] = Query(
        None, alias="species", description="Comma-separated list of species scientific names"
    ),
    bbox: Optional[str] = Query(None, description="Bounding box: min_lon,min_lat,max_lon,max_lat"),
    db: LanceDBManager = Depends(get_db),
):
    return await get_layer_data_for_type("breeding_sites", species_query=species, bbox=bbox, db_manager=db)
