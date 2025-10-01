"""
Geographic API endpoints for the CulicidaeLab server.

This module provides FastAPI router endpoints for retrieving geographic data and
spatial information related to arthropod vectors and vector-borne diseases. The
endpoints support various layer types and filtering options for spatial analysis
and mapping applications.

The module includes the following endpoints:
- GET /geo/{layer_type}: Retrieve geographic features for a specific layer type
  with optional spatial, temporal, and species-based filtering

All endpoints return GeoJSON-compliant data structures suitable for mapping
applications and geographic information systems (GIS). The endpoints support
bounding box filtering, date range filtering, and species-specific queries.
"""

from fastapi import APIRouter, Depends, Query, HTTPException, Path
import lancedb
from backend.services import database, geo_service
from backend.schemas.geo_schemas import GeoJSONFeatureCollection

router = APIRouter()

VALID_LAYER_TYPES = ["distribution", "observations", "modeled", "breeding_sites"]


@router.get("/geo/{layer_type}", response_model=GeoJSONFeatureCollection)
async def get_geographic_layer(
    layer_type: str = Path(..., description=f"Type of geographic layer. Valid types: {', '.join(VALID_LAYER_TYPES)}"),
    db: lancedb.DBConnection = Depends(database.get_db),
    species: str | None = Query(None, description="Comma-separated list of species scientific names to filter by"),
    bbox: str | None = Query(None, description="Bounding box filter: min_lon,min_lat,max_lon,max_lat"),
    start_date: str | None = Query(None, description="Start date for filtering (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="End date for filtering (YYYY-MM-DD)"),
):
    """
    Retrieve geographic features for a specific layer type with optional filtering.

    This endpoint provides access to various geographic data layers related to arthropod
    vectors and vector-borne diseases. Currently supports observation data with spatial,
    temporal, and species-based filtering capabilities.

    The endpoint returns GeoJSON FeatureCollection data that can be directly consumed
    by mapping libraries and GIS applications for visualization and spatial analysis.

    Args:
        layer_type (str): The type of geographic layer to retrieve. Must be one of:
            'distribution', 'observations', 'modeled', 'breeding_sites'.
        db (lancedb.DBConnection): Database connection for querying geographic data.
        species (str | None): Comma-separated list of species scientific names to filter by.
            If provided, only features for the specified species will be returned.
            Example: "Aedes aegypti,Anopheles gambiae,Culex quinquefasciatus".
        bbox (str | None): Bounding box filter in the format "min_lon,min_lat,max_lon,max_lat".
            Filters features to only include those within the specified geographic bounds.
            Example: "-122.4194,37.7749,-122.0808,37.9128" (San Francisco area).
        start_date (str | None): Start date for temporal filtering in YYYY-MM-DD format.
            Only features observed on or after this date will be included.
            Example: "2023-01-01".
        end_date (str | None): End date for temporal filtering in YYYY-MM-DD format.
            Only features observed on or before this date will be included.
            Example: "2023-12-31".

    Returns:
        GeoJSONFeatureCollection: A GeoJSON FeatureCollection containing the requested
            geographic features. Each feature includes geometry (Point) and properties
            with observation metadata such as species information, observation dates,
            and location details.

    Raises:
        HTTPException: If layer_type is invalid (400) or if bbox format is incorrect (400).

    Examples:
        Basic usage - retrieve all observation features:
        ```
        GET /geo/observations
        ```

        Filter by species:
        ```
        GET /geo/observations?species=Aedes%20aegypti,Anopheles%20gambiae
        ```

        Filter by geographic bounds (San Francisco):
        ```
        GET /geo/observations?bbox=-122.4194,37.7749,-122.0808,37.9128
        ```

        Filter by date range:
        ```
        GET /geo/observations?start_date=2023-01-01&end_date=2023-06-30
        ```

        Combined filters - species and location:
        ```
        GET /geo/observations?species=Aedes%20aegypti&bbox=-74.0,40.7,-71.0,45.0
        ```

        Combined filters - all parameters:
        ```
        GET /geo/observations?species=Culex%20quinquefasciatus
                            &bbox=-118.5,34.0,-118.1,34.3
                            &start_date=2023-03-01&end_date=2023-09-30
        ```
    """
    if layer_type not in VALID_LAYER_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid layer type. Valid types are: {', '.join(VALID_LAYER_TYPES)}",
        )

    species_list: list[str] | None = None
    if species:
        species_list = [s.strip() for s in species.split(",") if s.strip()]

    bbox_filter: tuple[float, float, float, float] | None = None
    if bbox:
        try:
            coords = [float(c.strip()) for c in bbox.split(",")]
            if len(coords) == 4:
                bbox_filter = (coords[0], coords[1], coords[2], coords[3])
            else:
                raise ValueError("Bounding box must have 4 coordinates.")
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid bbox format: {e}. Use min_lon,min_lat,max_lon,max_lat",
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
