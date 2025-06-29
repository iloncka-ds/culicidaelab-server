from pydantic import BaseModel
from typing import Dict, Any, List, Optional


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
    geojson_data: GeoJSONFeatureCollection
