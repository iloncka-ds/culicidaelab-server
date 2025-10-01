"""
Pydantic models for the Species service.

This module defines the schema models used for species data
validation in API endpoints.
"""

from pydantic import BaseModel


class SpeciesBase(BaseModel):
    """Base model for species information.

    Contains core species identification fields used across different
    species-related models.
    """

    id: str
    scientific_name: str
    common_name: str | None = None
    vector_status: str | None = None
    image_url: str | None = None


class SpeciesDetail(SpeciesBase):
    """Detailed species model with extended information.

    Extends the base species model with additional descriptive fields
    for comprehensive species information.
    """

    description: str | None = None
    key_characteristics: list[str] | None = None
    geographic_regions: list[str] | None = None
    related_diseases: list[str] | None = None
    habitat_preferences: list[str] | None = None


class SpeciesListResponse(BaseModel):
    """Response model for paginated species lists.

    Contains the total count and list of species for API responses.
    """

    count: int
    species: list[SpeciesBase]
