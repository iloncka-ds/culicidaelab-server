"""
Pydantic models for geographic data and GeoJSON structures.

This module defines the schema models used for handling geographic data,
GeoJSON structures, and map layer responses.
"""

from pydantic import BaseModel
from typing import Any


class GeoJSONGeometry(BaseModel):
    """GeoJSON geometry model.

    Represents the geometry component of a GeoJSON Feature,
    containing type and coordinates information.
    """

    type: str
    coordinates: Any


class GeoJSONFeature(BaseModel):
    """GeoJSON Feature model.

    Represents a complete GeoJSON Feature with type, properties, and geometry.
    Used for representing geographic features with associated data.
    """

    type: str = "Feature"
    properties: dict[str, Any]
    geometry: GeoJSONGeometry


class GeoJSONFeatureCollection(BaseModel):
    """GeoJSON FeatureCollection model.

    Represents a collection of GeoJSON Features for batch operations
    and API responses containing multiple geographic features.
    """

    type: str = "FeatureCollection"
    features: list[GeoJSONFeature]


class MapLayerResponse(BaseModel):
    """Response model for map layer data.

    Contains layer metadata and GeoJSON data for rendering map layers
    in the frontend application.
    """

    layer_type: str
    layer_name: str
    geojson_data: GeoJSONFeatureCollection
