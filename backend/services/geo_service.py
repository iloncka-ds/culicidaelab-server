import json
from typing import List, Optional, Tuple, Dict, Any
import lancedb
from backend.services.database import get_table
from backend.schemas.geo_schemas import GeoJSONFeatureCollection, GeoJSONFeature, GeoJSONGeometry
from shapely.geometry import box, Point
from datetime import datetime


def is_valid_date_str(date_str: str) -> bool:
    """Helper to validate YYYY-MM-DD date string format."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def get_geo_layer(
    db: lancedb.DBConnection,
    layer_type: str,
    species_list: Optional[List[str]] = None,
    bbox_filter: Optional[Tuple[float, float, float, float]] = None,
    start_date_str: Optional[str] = None,
    end_date_str: Optional[str] = None,
    limit: int = 10000,
) -> GeoJSONFeatureCollection:
    """Gets features for a specific layer, applying filters."""
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
                    type=record.get("geometry_type", "Point"), coordinates=record.get("coordinates")
                ),
            )
            filtered_features.append(feature)

        return GeoJSONFeatureCollection(features=filtered_features)

    except Exception as e:
        print(f"General error getting geo layer '{layer_type}': {e}")
        # Return empty collection on error
        return GeoJSONFeatureCollection(features=[])
