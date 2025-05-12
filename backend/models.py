from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union


# --- Species Models ---
class SpeciesBase(BaseModel):
    id: str
    scientific_name: str
    common_name: Optional[str] = None
    vector_status: Optional[str] = None
    image_url: Optional[str] = None


class SpeciesDetail(SpeciesBase):
    description: Optional[str] = None
    # These are stored as JSON strings in DB, parsed back here
    key_characteristics: Optional[List[str]] = None
    geographic_regions: Optional[List[str]] = None
    related_diseases: Optional[List[str]] = None
    habitat_preferences: Optional[List[str]] = None


class SpeciesListResponse(BaseModel):
    count: int
    species: List[SpeciesBase]  # Return only basic info for list


# --- Filter Options Model ---
class FilterOptions(BaseModel):
    species: List[str]
    regions: List[str]
    data_sources: List[str]


# --- GeoJSON Models (Simplified for API response) ---
# We'll reconstruct GeoJSON FeatureCollection on the backend side


class GeoJSONGeometry(BaseModel):
    type: str
    coordinates: Any  # Can be [lon, lat] or nested lists for polygons


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    properties: Dict[str, Any]
    geometry: GeoJSONGeometry


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]
