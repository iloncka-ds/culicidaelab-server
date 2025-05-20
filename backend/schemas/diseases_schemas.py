from pydantic import BaseModel, HttpUrl
from typing import List, Optional


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
    id: str  # From database document ID or a dedicated field

    class Config:
        from_attributes = True  # formerly orm_mode


class DiseaseListResponse(BaseModel):
    count: int
    diseases: List[Disease]