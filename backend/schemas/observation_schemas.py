"""
Pydantic models for the Observation service.

This module defines the schema models used for request/response validation
in the Observation service endpoints.
"""
from datetime import datetime
from typing import Dict, Optional, Any, List
from pydantic import BaseModel, Field, HttpUrl, validator


class ObservationBase(BaseModel):
    """Base model for Observation data."""
    species_id: str = Field(..., description="ID of the observed species")
    count: int = Field(..., gt=0, description="Number of observed specimens")
    location: Dict[str, float] = Field(
        ...,
        description="Geographic coordinates with 'lat' and 'lng' keys"
    )
    observed_at: str = Field(
        ...,
        description="ISO 8601 formatted timestamp when the observation was made (e.g., '2024-01-01T12:00:00Z')"
    )

    @validator('observed_at', pre=True)
    def parse_observed_at(cls, v):
        """Parse and validate the observed_at field."""
        if v is None:
            raise ValueError("observed_at is required")

        if isinstance(v, datetime):
            # If it's already a datetime, convert to ISO format string
            return v.isoformat()

        if isinstance(v, str):
            try:
                # Validate the string is a valid ISO 8601 datetime
                dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                return dt.isoformat()
            except (ValueError, TypeError):
                raise ValueError("Invalid datetime format. Use ISO 8601 format (e.g., '2024-01-01T12:00:00Z')")

        raise ValueError("observed_at must be a valid ISO 8601 datetime string")
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


class ObservationCreate(BaseModel):
    """Schema for creating a new observation.

    Attributes:
        species_id: ID of the observed species
        count: Number of specimens (must be > 0)
        location: Geographic coordinates with 'lat' and 'lng' keys
        observed_at: ISO 8601 formatted timestamp (e.g., '2024-01-01T12:00:00Z')
        notes: Additional notes about the observation (max 1000 chars)
        image_url: URL to an image of the observation if available
        metadata: Additional key-value pairs
    """
    species_id: str = Field(..., description="ID of the observed species")
    count: int = Field(..., gt=0, description="Number of observed specimens")
    location: Dict[str, float] = Field(
        ...,
        description="Geographic coordinates with 'lat' and 'lng' keys"
    )
    observed_at: str = Field(
        ...,
        description="ISO 8601 formatted timestamp (e.g., '2024-01-01T12:00:00Z')"
    )
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Additional notes about the observation"
    )
    image_url: Optional[str] = Field(
        None,
        description="URL to an image of the observation if available"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the observation"
    )

    @validator('observed_at', pre=True)
    def validate_observed_at(cls, v):
        """Validate and normalize the observed_at datetime."""
        if v is None:
            raise ValueError("observed_at is required")

        if isinstance(v, datetime):
            return v.isoformat()

        if isinstance(v, str):
            try:
                dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                return dt.isoformat()
            except (ValueError, TypeError):
                raise ValueError("Invalid datetime format. Use ISO 8601 format (e.g., '2024-01-01T12:00:00Z')")

        raise ValueError("observed_at must be a valid ISO 8601 datetime string")


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
    """Schema for an observation with system-generated fields.

    Attributes:
        id: Unique identifier for the observation
        species_id: ID of the observed species
        count: Number of observed specimens
        location: Geographic coordinates with 'lat' and 'lng' keys
        observed_at: ISO 8601 formatted timestamp when the observation was made
        notes: Additional notes about the observation
        image_url: URL to an image of the observation if available
        user_id: ID of the user who created the observation
        created_at: ISO 8601 timestamp when the observation was created
        updated_at: ISO 8601 timestamp when the observation was last updated
        metadata: Additional metadata about the observation
    """
    id: str = Field(..., description="Unique identifier for the observation")
    user_id: Optional[str] = Field(
        None,
        description="ID of the user who created the observation"
    )
    created_at: str = Field(
        ...,
        description="ISO 8601 timestamp when the observation was created (e.g., '2024-01-01T12:00:00Z')"
    )
    updated_at: str = Field(
        ...,
        description="ISO 8601 timestamp when the observation was last updated (e.g., '2024-01-01T12:00:00Z')"
    )

    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "species_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "count": 3,
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

    @validator('created_at', 'updated_at', pre=True)
    def parse_datetime(cls, v):
        """Parse datetime fields from various formats."""
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    @validator('id', 'user_id', pre=True)
    def parse_uuid(cls, v):
        """Parse UUID fields from various formats."""
        if v is not None:
            return str(v)
        return v


class ObservationListResponse(BaseModel):
    """Response model for a paginated list of observations.

    Attributes:
        count: Total number of observations matching the query
        observations: List of observation objects
    """
    count: int = Field(..., example=1, description="Total number of observations matching the query")
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
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "species_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                        "count": 3,
                        "location": {"lat": 40.7128, "lng": -74.0060},
                        "observed_at": "2024-01-01T12:00:00Z",
                        "notes": "Found near standing water",
                        "image_url": "https://example.com/image.jpg",
                        "user_id": "user123",
                        "created_at": "2024-01-01T12:00:00Z",
                        "updated_at": "2024-01-01T12:00:00Z",
                        "metadata": {"weather": "sunny", "temperature_c": 25}
                    }
                ]
            }
        }
