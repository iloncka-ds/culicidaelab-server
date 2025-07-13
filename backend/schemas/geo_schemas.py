from pydantic import BaseModel
from typing import Dict, Any, List


class GeoJSONGeometry(BaseModel):
    type: str
    coordinates: Any


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    properties: Dict[str, Any]
    geometry: GeoJSONGeometry


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]


class MapLayerResponse(BaseModel):
    layer_type: str
    layer_name: str
    geojson_data: GeoJSONFeatureCollection
