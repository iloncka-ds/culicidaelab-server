"""
Pydantic models for the Observation service.

This module defines the schema models used for request/response validation
in the Observation service endpoints.
"""

from typing import Any
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class Location(BaseModel):
    lat: float
    lng: float


class ObservationBase(BaseModel):
    type: str = "Feature"
    species_scientific_name: str
    count: int = Field(..., gt=0, description="Number of observed specimens")
    location: Location
    observed_at: str
    notes: str | None = None
    user_id: str | None = None
    location_accuracy_m: int | None = None
    data_source: str | None = None


class Observation(ObservationBase):
    id: UUID = Field(default_factory=uuid4)
    image_filename: str | None = None
    model_id: str | None = None
    confidence: float | None = None
    metadata: dict[str, Any] | None = {}


class ObservationListResponse(BaseModel):
    count: int
    observations: list[Observation]
