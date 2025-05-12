from backend.database.lancedb_manager import LanceDBManager
from typing import List, Optional, Dict, Any
import json


def filter_geojson_features(
    geojson_collection_str: str,
    species_list: Optional[List[str]] = None,
    bbox_str: Optional[str] = None,  # "min_lon,min_lat,max_lon,max_lat"
) -> Dict[str, Any]:
    """
    Filters features in a GeoJSON FeatureCollection string.
    Currently supports filtering by species.
    BBOX filtering requires parsing geometry.
    """
    if not geojson_collection_str:
        return {"type": "FeatureCollection", "features": []}

    geojson_data = json.loads(geojson_collection_str)
    original_features = geojson_data.get("features", [])

    if not original_features:
        return {"type": "FeatureCollection", "features": []}

    filtered_features = []

    # Parse BBOX if provided
    bbox = None
    if bbox_str:
        try:
            coords = [float(c.strip()) for c in bbox_str.split(",")]
            if len(coords) == 4:
                bbox = {"min_lon": coords[0], "min_lat": coords[1], "max_lon": coords[2], "max_lat": coords[3]}
        except ValueError:
            print(f"Warning: Invalid BBOX string format: {bbox_str}")
            bbox = None

    for feature in original_features:
        props = feature.get("properties", {})
        geometry = feature.get("geometry", {})

        # Species filter
        if species_list:
            feature_species = props.get("species")
            if not feature_species or feature_species not in species_list:
                continue  # Skip if species doesn't match

        # BBOX filter (basic point-in-bbox for Point geometries)
        if bbox and geometry and geometry.get("type") == "Point":
            coords = geometry.get("coordinates")  # [lon, lat]
            if not (
                coords
                and len(coords) == 2
                and bbox["min_lon"] <= coords[0] <= bbox["max_lon"]
                and bbox["min_lat"] <= coords[1] <= bbox["max_lat"]
            ):
                continue  # Skip if point outside bbox
        # TODO: Add BBOX filtering for Polygons (more complex: check if polygon intersects bbox)

        filtered_features.append(feature)

    return {"type": "FeatureCollection", "features": filtered_features}


class GeoService:
    def __init__(self, db_manager: LanceDBManager):
        self.db_manager = db_manager

    async def get_map_layer_data(
        self, layer_type: str, species: Optional[List[str]] = None, bbox_filter: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        map_layers_table = await self.db_manager.get_table("map_layers")
        if not map_layers_table:
            return None

        # Find the layer entry for the given type.
        # This assumes one entry per layer_type in the 'map_layers' table.
        # If multiple named layers of the same type exist, this needs refinement.
        query_builder = map_layers_table.search().where(f"layer_type = '{layer_type}'")

        # If layer data is pre-filtered by 'contained_species' in LanceDB table
        # this could be an optimization, but requires exact match logic for list elements.
        # For now, fetch the whole GeoJSON and filter in Python.

        results_df = await query_builder.limit(1).to_pandas()

        if results_df.empty:
            return None

        layer_record = results_df.iloc[0].to_dict()
        geojson_str = layer_record.get("geojson_data")

        if not geojson_str:
            return {"type": "FeatureCollection", "features": []}

        # Filter the GeoJSON data in Python
        filtered_geojson = filter_geojson_features(geojson_str, species_list=species, bbox_str=bbox_filter)
        return filtered_geojson
