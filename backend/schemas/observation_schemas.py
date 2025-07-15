"""
Pydantic models for the Observation service.

This module defines the schema models used for request/response validation
in the Observation service endpoints.
"""
from typing import Dict, Optional, Any, List
from pydantic import BaseModel, Field


class Location(BaseModel):
    lat: float
    lng: float

class ObservationBase(BaseModel):
    type: str = "Feature"
    species_scientific_name: str
    count: int = Field(..., gt=0, description="Number of observed specimens")
    location: Location
    observed_at: str
    notes: Optional[str] = None
    user_id: Optional[str] = None
    location_accuracy_m: Optional[int] = None
    data_source: Optional[str] = None

class Observation(ObservationBase):
    image_filename: Optional[str] = None
    model_id: Optional[str] = None
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = {}


class ObservationListResponse(BaseModel):
    count: int
    observations: List[Observation]