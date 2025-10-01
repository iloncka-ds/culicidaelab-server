"""
Pydantic models for the Observation service.

This module defines the schema models used for request/response validation
in the Observation service endpoints.
"""

from typing import Any
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class Location(BaseModel):
    """Geographic location model.

    Represents latitude and longitude coordinates for observations.
    """

    lat: float
    lng: float


class ObservationBase(BaseModel):
    """Base model for observation data.

    Contains core observation fields used for creating and validating
    observation records.
    """

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
    """Complete observation model with unique identifier.

    Extends ObservationBase with system-generated fields for
    storing complete observation records.
    """

    id: UUID = Field(default_factory=uuid4)
    image_filename: str | None = None
    model_id: str | None = None
    confidence: float | None = None
    metadata: dict[str, Any] | None = {}


class ObservationListResponse(BaseModel):
    """Response model for paginated observation lists.

    Contains the total count and list of observations for API responses.
    """

    count: int
    observations: list[Observation]
