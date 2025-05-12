from pydantic import BaseModel
from typing import Dict, Any, List, Optional


# Generic GeoJSON Feature and FeatureCollection (can be more specific if needed)
class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    properties: Dict[str, Any]
    geometry: Dict[str, Any]


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]


class MapLayerResponse(BaseModel):
    layer_type: str
    layer_name: str
    geojson_data: GeoJSONFeatureCollection  # Parsed GeoJSON
