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

# class SpeciesBase(BaseModel):
#     id: str
#     scientific_name: str
#     common_name: Optional[str] = None
#     vector_status: Optional[str] = None
#     image_url: Optional[str] = None


class SpeciesDetail(SpeciesBase):
    description: Optional[str] = None
    # These are stored as JSON strings in DB, parsed back here
    key_characteristics: Optional[List[str]] = None
    geographic_regions: Optional[List[str]] = None
    related_diseases: Optional[List[str]] = None
    habitat_preferences: Optional[List[str]] = None


class Species(SpeciesBase):
    id: str

    class Config:
        from_attributes = True


class FilterOptionsResponse(BaseModel):
    species: List[str]
    regions: List[str]
    data_sources: List[str]
