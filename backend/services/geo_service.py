# from backend.database.lancedb_manager import LanceDBManager
# from typing import List, Optional, Dict, Any
# import json


# def filter_geojson_features(
#     geojson_collection_str: str,
#     species_list: Optional[List[str]] = None,
#     bbox_str: Optional[str] = None,  # "min_lon,min_lat,max_lon,max_lat"
# ) -> Dict[str, Any]:
#     """
#     Filters features in a GeoJSON FeatureCollection string.
#     Currently supports filtering by species.
#     BBOX filtering requires parsing geometry.
#     """
#     if not geojson_collection_str:
#         return {"type": "FeatureCollection", "features": []}

#     geojson_data = json.loads(geojson_collection_str)
#     original_features = geojson_data.get("features", [])

#     if not original_features:
#         return {"type": "FeatureCollection", "features": []}

#     filtered_features = []

#     # Parse BBOX if provided
#     bbox = None
#     if bbox_str:
#         try:
#             coords = [float(c.strip()) for c in bbox_str.split(",")]
#             if len(coords) == 4:
#                 bbox = {"min_lon": coords[0], "min_lat": coords[1], "max_lon": coords[2], "max_lat": coords[3]}
#         except ValueError:
#             print(f"Warning: Invalid BBOX string format: {bbox_str}")
#             bbox = None

#     for feature in original_features:
#         props = feature.get("properties", {})
#         geometry = feature.get("geometry", {})

#         # Species filter
#         if species_list:
#             feature_species = props.get("species")
#             if not feature_species or feature_species not in species_list:
#                 continue  # Skip if species doesn't match

#         # BBOX filter (basic point-in-bbox for Point geometries)
#         if bbox and geometry and geometry.get("type") == "Point":
#             coords = geometry.get("coordinates")  # [lon, lat]
#             if not (
#                 coords
#                 and len(coords) == 2
#                 and bbox["min_lon"] <= coords[0] <= bbox["max_lon"]
#                 and bbox["min_lat"] <= coords[1] <= bbox["max_lat"]
#             ):
#                 continue  # Skip if point outside bbox
#         # TODO: Add BBOX filtering for Polygons (more complex: check if polygon intersects bbox)

#         filtered_features.append(feature)

#     return {"type": "FeatureCollection", "features": filtered_features}


# class GeoService:
#     def __init__(self, db_manager: LanceDBManager):
#         self.db_manager = db_manager

#     async def get_map_layer_data(
#         self, layer_type: str, species: Optional[List[str]] = None, bbox_filter: Optional[str] = None
#     ) -> Optional[Dict[str, Any]]:
#         map_layers_table = await self.db_manager.get_table("map_layers")
#         if not map_layers_table:
#             return None

#         # Find the layer entry for the given type.
#         # This assumes one entry per layer_type in the 'map_layers' table.
#         # If multiple named layers of the same type exist, this needs refinement.
#         query_builder = map_layers_table.search().where(f"layer_type = '{layer_type}'")

#         # If layer data is pre-filtered by 'contained_species' in LanceDB table
#         # this could be an optimization, but requires exact match logic for list elements.
#         # For now, fetch the whole GeoJSON and filter in Python.

#         results_df = await query_builder.limit(1).to_pandas()

#         if results_df.empty:
#             return None

#         layer_record = results_df.iloc[0].to_dict()
#         geojson_str = layer_record.get("geojson_data")

#         if not geojson_str:
#             return {"type": "FeatureCollection", "features": []}

#         # Filter the GeoJSON data in Python
#         filtered_geojson = filter_geojson_features(geojson_str, species_list=species, bbox_str=bbox_filter)
#         return filtered_geojson

import json
from typing import List, Optional, Tuple
import lancedb
from backend.services.database import get_table
from backend.models import GeoJSONFeatureCollection, GeoJSONFeature, GeoJSONGeometry
from shapely.geometry import box, Point, shape  # For bbox filtering


def _db_record_to_geojson_feature(record: dict) -> Optional[GeoJSONFeature]:
    """Converts a LanceDB geo_features record back to a GeoJSON Feature."""
    properties_json = record.get("properties_json")
    if not properties_json:
        return None  # Cannot reconstruct without properties

    try:
        properties = json.loads(properties_json)
    except json.JSONDecodeError:
        print(f"Warning: Could not decode properties_json: {properties_json}")
        return None

    # Reconstruct geometry (simple point/polygon for now)
    geom_type = record.get("geometry_type")
    coordinates = None
    if geom_type == "Point" and record.get("lon") is not None and record.get("lat") is not None:
        coordinates = [record["lon"], record["lat"]]
    elif geom_type == "Polygon":
        # We didn't store full polygon coordinates back, only bbox/centroid
        # We MUST retrieve the original properties to get the geometry back accurately
        # The properties_json should contain the original geometry! Let's check.
        if "geometry" in properties and isinstance(properties.get("geometry"), dict):
            geom_dict_from_props = properties["geometry"]  # This assumes we stored it - WE DIDN'T in setup script
            geom_type_from_props = geom_dict_from_props.get("type")
            coords_from_props = geom_dict_from_props.get("coordinates")
            if geom_type_from_props and coords_from_props:
                geom_type = geom_type_from_props
                coordinates = coords_from_props
        # Fallback: If not stored in props, we cannot reconstruct polygons accurately here.
        # We NEED to store the full geometry in LanceDB or retrieve it differently.
        # Let's modify setup_lancedb.py later. For now, return None for polygons.
        if not coordinates:
            # print(f"Warning: Cannot reconstruct Polygon geometry for record. Need original geometry.")
            return None  # Cannot reconstruct polygon geometry from current DB schema accurately

    if coordinates is None:
        return None  # Skip features where geometry can't be determined

    return GeoJSONFeature(
        properties=properties,  # Use the full original properties
        geometry=GeoJSONGeometry(type=geom_type, coordinates=coordinates),
    )


# --- Filtering Logic ---

def filter_features(
    features: List[dict],  # List of raw dicts from LanceDB
    species: Optional[List[str]] = None,
    bbox: Optional[Tuple[float, float, float, float]] = None,  # (min_lon, min_lat, max_lon, max_lat)
    # date_range: Optional[Tuple[str, str]] = None # TODO: Add date filtering
) -> List[dict]:
    """Filters raw LanceDB records in Python."""
    filtered = features

    # 1. Species Filter
    if species:
        # Handle features where species might be None (like some breeding sites)
        filtered = [f for f in filtered if f.get("species") is None or f.get("species") in species]

    # 2. Bbox Filter
    if bbox:
        min_lon, min_lat, max_lon, max_lat = bbox
        bbox_polygon = box(min_lon, min_lat, max_lon, max_lat)
        spatially_filtered = []
        for f in filtered:
            geom_json = f.get("geometry_json")
            if not geom_json: continue
            try:
                geom_dict = json.loads(geom_json)
                feature_geom = shape(geom_dict) # Use shapely to parse full geometry
                if bbox_polygon.intersects(feature_geom): # Use intersects for points and polygons
                    spatially_filtered.append(f)
            except Exception as e:
                # print(f"Warning: Could not parse geometry for bbox filtering: {e}")
                pass # Skip if geometry is invalid

        filtered = spatially_filtered

    # 3. Date Range Filter (Placeholder)
    # if date_range:
    #    start_date, end_date = date_range
    #    # Filter based on obs_date or other relevant date field
    #    pass

    return filtered


# --- Service Function ---


def get_geo_layer(
    db: lancedb.DBConnection,
    layer_type: str,
    species_list: Optional[List[str]] = None,
    bbox_filter: Optional[Tuple[float, float, float, float]] = None,
    limit: int = 5000,  # Limit records retrieved from DB before Python filtering
) -> GeoJSONFeatureCollection:
    """Gets features for a specific layer, applying filters."""

    features_out: List[GeoJSONFeature] = []
    try:
        tbl = get_table(db, "geo_features")

        # --- LanceDB Filtering (if possible) ---
        # Build a basic WHERE clause
        # Note: LanceDB SQL support is evolving. Test these clauses.
        where_clauses = [f"layer_type = '{layer_type}'"]
        # Cannot directly filter by species list in WHERE easily unless LanceDB supports IN operator well.
        # Bbox filtering using SQL is complex without spatial indexing/functions.

        query_str = " AND ".join(where_clauses) if where_clauses else None

        # Retrieve raw data (potentially more than needed, up to limit)
        raw_records = (
            tbl.search().where(query_str).limit(limit).to_list() if query_str else tbl.search().limit(limit).to_list()
        )
        print(f"Retrieved {len(raw_records)} raw records for layer '{layer_type}' from DB.")

        # --- Python Filtering ---
        filtered_records = filter_features(raw_records, species=species_list, bbox=bbox_filter)
        print(f"Filtered down to {len(filtered_records)} records in Python.")

        # --- Convert to GeoJSON Features ---
        for record in filtered_records:
            feature = _db_record_to_geojson_feature(record)
            if feature:
                features_out.append(feature)

    except ValueError as e:  # Catch table not found from get_table
        print(f"Value error getting geo layer {layer_type}: {e}")
        # Return empty collection
    except Exception as e:
        print(f"Error getting geo layer {layer_type}: {e}")
        # Optionally raise or return empty collection

    return GeoJSONFeatureCollection(features=features_out)
