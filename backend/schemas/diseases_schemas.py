"""
Pydantic models for the Disease service.

This module defines the schema models used for request/response validation
in the Disease service endpoints.
"""

from pydantic import BaseModel


class DiseaseBase(BaseModel):
    """Base model for disease information.

    Contains common fields that can be shared between request and response models.
    """

    name: str | None = None
    description: str | None = None
    symptoms: str | None = None
    treatment: str | None = None
    prevention: str | None = None
    prevalence: str | None = None
    image_url: str | None = None
    vectors: list[str] | None = []


class Disease(DiseaseBase):
    """Complete disease model with unique identifier.

    Used for responses that include the database ID of the disease.
    """

    id: str

    class Config:
        from_attributes = True


class DiseaseListResponse(BaseModel):
    """Response model for paginated disease lists.

    Contains the total count and list of diseases for API responses.
    """

    count: int
    diseases: list[Disease]
