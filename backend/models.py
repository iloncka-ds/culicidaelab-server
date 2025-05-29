from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


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


# Observation Model
class ObservationBase(BaseModel):
    species_id: str
    count: int = Field(..., gt=0, description="Number of observed specimens")
    location: Dict[str, float]  # {lat: float, lng: float}
    observed_at: str  # ISO 8601 datetime string
    notes: Optional[str] = None
    image_url: Optional[str] = None
    user_id: Optional[str] = None  # Will be populated from auth token
    metadata: Optional[Dict[str, Any]] = {}


class Observation(ObservationBase):
    id: str
    created_at: str  # ISO 8601 datetime string
    updated_at: str  # ISO 8601 datetime string


class ObservationCreate(ObservationBase):
    pass


class ObservationListResponse(BaseModel):
    count: int
    observations: List[Observation]


# Disease Models
class DiseaseBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    symptoms: Optional[str] = None
    treatment: Optional[str] = None
    prevention: Optional[str] = None
    prevalence: Optional[str] = None
    image_url: Optional[str] = None
    vectors: Optional[List[str]] = []  # List of vector species IDs


class Disease(DiseaseBase):
    id: str


class DiseaseListResponse(BaseModel):
    count: int
    diseases: List[Disease]


class DiseaseDetail(Disease):
    pass