"""
Pydantic models for the Observation service.

This module defines the schema models used for request/response validation
in the Observation service endpoints.
"""
from datetime import datetime
from typing import Dict, Optional, Any, List
from pydantic import BaseModel, Field, HttpUrl, validator
from uuid import UUID


class ObservationBase(BaseModel):
    """Base model for Observation data."""
    species_id: str = Field(..., description="ID of the observed species")
    count: int = Field(..., gt=0, description="Number of observed specimens")
    location: Dict[str, float] = Field(
        ...,
        description="Geographic coordinates with 'lat' and 'lng' keys"
    )
    observed_at: datetime = Field(
        ...,
        description="Timestamp when the observation was made"
    )
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Additional notes about the observation"
    )
    image_url: Optional[HttpUrl] = Field(
        None,
        description="URL to an image of the observation if available"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the observation"
    )

    @validator('location')
    def validate_location(cls, v):
        """Validate that location has both latitude and longitude."""
        if 'lat' not in v or 'lng' not in v:
            raise ValueError("Location must contain both 'lat' and 'lng' keys")
        if not (-90 <= v['lat'] <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= v['lng'] <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v


class ObservationCreate(ObservationBase):
    """Schema for creating a new observation."""
    pass


class ObservationUpdate(BaseModel):
    """Schema for updating an existing observation."""
    species_id: Optional[str] = Field(
        None,
        description="ID of the observed species"
    )
    count: Optional[int] = Field(
        None,
        gt=0,
        description="Number of observed specimens"
    )
    location: Optional[Dict[str, float]] = Field(
        None,
        description="Geographic coordinates with 'lat' and 'lng' keys"
    )
    observed_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the observation was made"
    )
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Additional notes about the observation"
    )
    image_url: Optional[HttpUrl] = Field(
        None,
        description="URL to an image of the observation if available"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata about the observation"
    )


class Observation(ObservationBase):
    """Schema for an observation with system-generated fields."""
    id: UUID = Field(..., description="Unique identifier for the observation")
    user_id: Optional[UUID] = Field(
        None,
        description="ID of the user who created the observation"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the observation was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the observation was last updated"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "species_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "count": 5,
                "location": {"lat": 40.7128, "lng": -74.0060},
                "observed_at": "2024-01-01T12:00:00Z",
                "notes": "Found near standing water",
                "image_url": "https://example.com/image.jpg",
                "user_id": "user123",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z",
                "metadata": {"weather": "sunny", "temperature_c": 25}
            }
        }


class ObservationListResponse(BaseModel):
    """Response model for paginated list of observations."""
    count: int = Field(..., description="Total number of observations")
    observations: List[Observation] = Field(
        ...,
        description="List of observation objects"
    )

    class Config:
        schema_extra = {
            "example": {
                "count": 1,
                "observations": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "species_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                        "count": 5,
                        "location": {"lat": 40.7128, "lng": -74.0060},
                        "observed_at": "2024-01-01T12:00:00Z",
                        "notes": "Found near standing water",
                        "image_url": "https://example.com/image.jpg",
                        "user_id": "user123",
                        "created_at": "2024-01-01T12:00:00Z",
                        "updated_at": "2024-01-01T12:00:00Z",
                        "metadata": {}
                    }
                ]
            }
        }
