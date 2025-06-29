from pydantic import BaseModel, HttpUrl
from typing import List, Optional


class SpeciesBase(BaseModel):
    scientific_name: Optional[str] = None
    common_name: Optional[str] = None
    vector_status: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    description: Optional[str] = None
    key_characteristics: Optional[List[str]] = []
    geographic_regions: Optional[List[str]] = []
    related_diseases: Optional[List[str]] = []
    related_diseases_info: Optional[List[str]] = []
    habitat_preferences: Optional[List[str]] = []


class Species(SpeciesBase):
    id: str

    class Config:
        from_attributes = True


class FilterOptionsResponse(BaseModel):
    species: List[str]
    regions: List[str]
    data_sources: List[str]
