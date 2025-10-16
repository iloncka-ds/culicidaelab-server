"""
Geographic data service for handling spatial queries and filtering.

This module provides functionality for querying and filtering geographic data,
particularly observation data with spatial and temporal filtering capabilities.
It supports bounding box filtering, date range filtering, and species-based
filtering for geographic visualization.

Example:
    >>> from backend.services.geo_service import get_geo_layer
    >>> from backend.services.database import get_db
    >>> db = get_db()
    >>> features = get_geo_layer(db, "observations", species_list=["Aedes aegypti"])
"""

import lancedb
from backend.services.database import get_table
from backend.schemas.geo_schemas import GeoJSONFeatureCollection, GeoJSONFeature, GeoJSONGeometry
from shapely.geometry import box, Point
from datetime import datetime


def is_valid_date_str(date_str: str) -> bool:
    """Validate if a string represents a valid YYYY-MM-DD date format.

    This helper function checks if the provided string can be parsed as a date
    in the expected format used throughout the application.

    Args:
        date_str (str): The date string to validate.

    Returns:
        bool: True if the string is a valid YYYY-MM-DD date, False otherwise.

    Example:
        >>> is_valid_date_str("2023-12-25")
        True
        >>> is_valid_date_str("invalid-date")
        False
    """
    if not isinstance(date_str, str):
        return False
    
    # Check exact format: YYYY-MM-DD (10 characters, specific pattern)
    if len(date_str) != 10 or date_str[4] != '-' or date_str[7] != '-':
        return False
    
    try:
        # Parse the date and ensure it's valid
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
        # Ensure the parsed date formats back to the same string (strict format check)
        return parsed_date.strftime("%Y-%m-%d") == date_str
    except (ValueError, TypeError):
        return False


def get_geo_layer(
    db: lancedb.DBConnection,
    layer_type: str,
    species_list: list[str] | None = None,
    bbox_filter: tuple[float, float, float, float] | None = None,
    start_date_str: str | None = None,
    end_date_str: str | None = None,
    limit: int = 10000,
) -> GeoJSONFeatureCollection:
    """Retrieve geographic features for a specific layer with optional filtering.

    This function queries observation data and applies multiple filters including
    species, bounding box, and date range filters. It returns GeoJSON formatted
    features suitable for mapping applications.

    Args:
        db (lancedb.DBConnection): The database connection object.
        layer_type (str): The type of layer to retrieve. Currently supports
            "observations". Other types return empty collections.
        species_list (list[str] | None, optional): List of species scientific
            names to filter by. If None, no species filtering is applied.
        bbox_filter (tuple[float, float, float, float] | None, optional): A
            bounding box as (min_lon, min_lat, max_lon, max_lat). If None,
            no spatial filtering is applied.
        start_date_str (str | None, optional): Start date in YYYY-MM-DD format.
            If None, no start date filtering is applied.
        end_date_str (str | None, optional): End date in YYYY-MM-DD format.
            If None, no end date filtering is applied.
        limit (int, optional): Maximum number of records to return.
            Defaults to 10000.

    Returns:
        GeoJSONFeatureCollection: A GeoJSON FeatureCollection containing the
            filtered observation features with their properties and geometry.

    Example:
        >>> from backend.services.database import get_db
        >>> db = get_db()
        >>> # Get all Aedes aegypti observations in a specific region
        >>> features = get_geo_layer(
        ...     db,
        ...     "observations",
        ...     species_list=["Aedes aegypti"],
        ...     bbox_filter=(-74.1, 40.6, -71.9, 41.3),  # NYC area
        ...     start_date_str="2023-01-01",
        ...     end_date_str="2023-12-31"
        ... )
        >>> print(len(features.features))  # Number of observations
    """
    if layer_type != "observations":
        # Returns empty collection for unsupported layer types for now.
        return GeoJSONFeatureCollection(features=[])

    try:
        tbl = get_table(db, "observations")

        query = tbl.search()
        if species_list:
            species_filter = " OR ".join([f"species_scientific_name = '{s}'" for s in species_list])
            query = query.where(species_filter)

        all_records = query.limit(limit).to_list()

        # Perform filtering in Python for criteria not easily handled by LanceDB FTS
        filtered_features = []
        bbox_polygon = box(*bbox_filter) if bbox_filter else None
        start_date_obj = (
            datetime.strptime(start_date_str, "%Y-%m-%d").date()
            if start_date_str and is_valid_date_str(start_date_str)
            else None
        )
        end_date_obj = (
            datetime.strptime(end_date_str, "%Y-%m-%d").date()
            if end_date_str and is_valid_date_str(end_date_str)
            else None
        )

        for record in all_records:
            # Bounding Box Filter
            if bbox_polygon and record.get("coordinates"):
                point = Point(record["coordinates"])
                if not bbox_polygon.contains(point):
                    continue

            # Date Range Filter
            if (start_date_obj or end_date_obj) and record.get("observed_at"):
                try:
                    record_date = datetime.strptime(record["observed_at"], "%Y-%m-%d").date()
                    if start_date_obj and record_date < start_date_obj:
                        continue
                    if end_date_obj and record_date > end_date_obj:
                        continue
                except (ValueError, TypeError):
                    continue

            feature = GeoJSONFeature(
                properties={k: v for k, v in record.items() if k not in ["geometry_type", "coordinates"]},
                geometry=GeoJSONGeometry(
                    type=record.get("geometry_type", "Point"),
                    coordinates=record.get("coordinates"),
                ),
            )
            filtered_features.append(feature)

        return GeoJSONFeatureCollection(features=filtered_features)

    except Exception as e:
        print(f"General error getting geo layer '{layer_type}': {e}")
        # Return empty collection on error
        return GeoJSONFeatureCollection(features=[])
