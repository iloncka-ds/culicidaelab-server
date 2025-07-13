from pydantic import BaseModel
from typing import List, Optional


class DiseaseBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    symptoms: Optional[str] = None
    treatment: Optional[str] = None
    prevention: Optional[str] = None
    prevalence: Optional[str] = None
    image_url: Optional[str] = None
    vectors: Optional[List[str]] = []


class Disease(DiseaseBase):
    id: str

    class Config:
        from_attributes = True


class DiseaseListResponse(BaseModel):
    count: int
    diseases: List[Disease]
