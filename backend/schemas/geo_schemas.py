from pydantic import BaseModel
from typing import Any


class GeoJSONGeometry(BaseModel):
    type: str
    coordinates: Any


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    properties: dict[str, Any]
    geometry: GeoJSONGeometry


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: list[GeoJSONFeature]


class MapLayerResponse(BaseModel):
    layer_type: str
    layer_name: str
    geojson_data: GeoJSONFeatureCollection
