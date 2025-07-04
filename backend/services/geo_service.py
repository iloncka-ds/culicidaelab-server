import json
from typing import List, Optional, Tuple, Dict, Any
import lancedb
from backend.services.database import get_table
from backend.models import GeoJSONFeatureCollection, GeoJSONFeature, GeoJSONGeometry
from shapely.geometry import box, Point, shape
from datetime import datetime


def is_valid_date_str(date_str: str) -> bool:
    """Helper to validate YYYY-MM-DD date string format."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def _db_record_to_geojson_feature(record: dict) -> Optional[GeoJSONFeature]:
    """Converts a LanceDB geo_features record back to a GeoJSON Feature."""
    properties_json = record.get("properties_json")
    geometry_json = record.get("geometry_json")

    if not properties_json or not geometry_json:
        return None

    try:
        properties = json.loads(properties_json)
        geometry_dict = json.loads(geometry_json)
    except json.JSONDecodeError as e:
        return None

    if not isinstance(geometry_dict, dict) or "type" not in geometry_dict or "coordinates" not in geometry_dict:
        return None

    return GeoJSONFeature(
        properties=properties,
        geometry=GeoJSONGeometry(type=geometry_dict["type"], coordinates=geometry_dict["coordinates"]),
    )




def filter_features(
    features: List[dict],
    layer_type: str,
    species: Optional[List[str]] = None,
    bbox: Optional[Tuple[float, float, float, float]] = None,
    date_range_str: Optional[Tuple[Optional[str], Optional[str]]] = None,
) -> List[dict]:
    """Filters raw LanceDB records in Python."""
    filtered = features

    if species:
        filtered = [
            f for f in filtered if f.get("species") is None or f.get("species") == "" or f.get("species") in species
        ]

    if bbox:
        min_lon, min_lat, max_lon, max_lat = bbox
        bbox_polygon = box(min_lon, min_lat, max_lon, max_lat)
        spatially_filtered = []
        for f in filtered:
            geom_json = f.get("geometry_json")
            if not geom_json:
                continue
            try:
                geom_dict = json.loads(geom_json)
                feature_geom = shape(geom_dict)
                if bbox_polygon.intersects(feature_geom):
                    spatially_filtered.append(f)
            except Exception:
                pass
        filtered = spatially_filtered

    if date_range_str and (date_range_str[0] or date_range_str[1]):
        s_date_str, e_date_str = date_range_str
        start_date_obj, end_date_obj = None, None
        try:
            if s_date_str:
                start_date_obj = datetime.strptime(s_date_str, "%Y-%m-%d").date()
            if e_date_str:
                end_date_obj = datetime.strptime(e_date_str, "%Y-%m-%d").date()
        except ValueError:
            print(f"Warning: Invalid date format in date_range_str: {date_range_str}. Skipping date filter.")
            return filtered

        date_key_map = {
            "observations": "observation_date",
            "distribution": "last_updated",
            "modeled": "run_date",
            "breeding_sites": "last_inspected",
        }
        date_property_key = date_key_map.get(layer_type)

        if not date_property_key:
            print(
                f"Warning: No date property key defined for layer_type '{layer_type}'. Date filter not applied for this layer."
            )
        else:
            date_filtered_batch = []
            for f_dict in filtered:
                props_json = f_dict.get("properties_json")
                if not props_json:
                    continue

                try:
                    props = json.loads(props_json)
                    feature_date_str = props.get(date_property_key)
                    if not feature_date_str:
                        continue

                    feature_date = datetime.strptime(feature_date_str, "%Y-%m-%d").date()

                    passes_date_filter = True
                    if start_date_obj and feature_date < start_date_obj:
                        passes_date_filter = False
                    if end_date_obj and feature_date > end_date_obj:
                        passes_date_filter = False

                    if passes_date_filter:
                        date_filtered_batch.append(f_dict)
                except (json.JSONDecodeError, ValueError):
                    continue
            filtered = date_filtered_batch

    return filtered




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

    features_out: List[GeoJSONFeature] = []
    try:
        tbl = get_table(db, "geo_features")
        if tbl is None:
            print(f"Error: Table 'geo_features' not found or could not be opened.")
            return GeoJSONFeatureCollection(features=[])

        where_clauses = [f"layer_type = '{layer_type}'"]

        query_str = f"layer_type = '{layer_type}'"

        query = tbl.search().where(query_str)


        raw_records = query.limit(limit).to_list()

        print(f"Retrieved {len(raw_records)} raw records for layer '{layer_type}' (filter: {query_str}) from DB.")

        date_range_tuple = (start_date_str, end_date_str)
        filtered_records = filter_features(
            raw_records,
            layer_type=layer_type,
            species=species_list,
            bbox=bbox_filter,
            date_range_str=date_range_tuple,
        )
        print(f"Filtered down to {len(filtered_records)} records in Python.")

        for record in filtered_records:
            feature = _db_record_to_geojson_feature(record)
            if feature:
                features_out.append(feature)

    except ValueError as e:
        print(f"Value error getting geo layer {layer_type}: {e}")
    except Exception as e:
        print(f"General error getting geo layer {layer_type}: {e}")
        import traceback

        traceback.print_exc()

    return GeoJSONFeatureCollection(features=features_out)
