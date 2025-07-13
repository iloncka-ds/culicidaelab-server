"""
Pydantic models for the Observation service.

This module defines the schema models used for request/response validation
in the Observation service endpoints.
"""
from typing import Dict, Optional, Any, List
from pydantic import BaseModel, Field


class ObservationBase(BaseModel):
    species_id: str
    count: int = Field(..., gt=0, description="Number of observed specimens")
    location: Dict[str, float]
    observed_at: str
    notes: Optional[str] = None
    image_url: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


class Observation(ObservationBase):
    id: str
    created_at: str
    updated_at: str


class ObservationCreate(ObservationBase):
    pass


class ObservationListResponse(BaseModel):
    count: int
    observations: List[Observation]