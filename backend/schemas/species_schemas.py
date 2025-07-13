from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional


class SpeciesBase(BaseModel):
    id: str
    scientific_name: str
    common_name: Optional[str] = None
    vector_status: Optional[str] = None
    image_url: Optional[str] = None


class SpeciesDetail(SpeciesBase):
    description: Optional[str] = None
    key_characteristics: Optional[List[str]] = None
    geographic_regions: Optional[List[str]] = None
    related_diseases: Optional[List[str]] = None
    habitat_preferences: Optional[List[str]] = None


class SpeciesListResponse(BaseModel):
    count: int
    species: List[SpeciesBase]


