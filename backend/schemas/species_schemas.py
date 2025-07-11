from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional


class SpeciesBase(BaseModel):
    """Base model for species data.
    
    Attributes:
        scientific_name: The scientific name of the species
        common_name: Common name of the species
        vector_status: Disease vector status (e.g., 'primary', 'secondary')
        image_url: URL to an image of the species
        description: Detailed description of the species
        key_characteristics: List of distinguishing features
        geographic_regions: List of regions where the species is found
        related_diseases: List of disease IDs this species can transmit
        habitat_preferences: List of preferred habitats
    """
    scientific_name: str = Field(..., description="Scientific name of the species")
    common_name: Optional[str] = Field(None, description="Common name of the species")
    vector_status: Optional[str] = Field(None, description="Disease vector status (e.g., 'primary', 'secondary')")
    image_url: Optional[str] = Field(None, description="URL to an image of the species")
    
    class Config:
        json_encoders = {
            'HttpUrl': lambda v: str(v) if v else None
        }


class SpeciesDetail(SpeciesBase):
    """Detailed species information including all attributes."""
    description: Optional[str] = Field(None, description="Detailed description of the species")
    key_characteristics: List[str] = Field(
        default_factory=list, 
        description="List of distinguishing features"
    )
    geographic_regions: List[str] = Field(
        default_factory=list,
        description="List of regions where the species is found"
    )
    related_diseases: List[str] = Field(
        default_factory=list,
        description="List of disease IDs this species can transmit"
    )
    habitat_preferences: List[str] = Field(
        default_factory=list,
        description="List of preferred habitats"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "id": "species-123",
                "scientific_name": "Aedes aegypti",
                "common_name": "Yellow fever mosquito",
                "vector_status": "primary",
                "image_url": "https://example.com/aedes_aegypti.jpg",
                "description": "A mosquito that can spread dengue, chikungunya, Zika, and yellow fever.",
                "key_characteristics": [
                    "Black and white striped legs",
                    "Lyre-shaped marking on thorax"
                ],
                "geographic_regions": ["tropical", "subtropical"],
                "related_diseases": ["dengue", "zika", "yellow-fever"],
                "habitat_preferences": ["urban areas", "standing water"]
            }
        }


class Species(SpeciesBase):
    """Basic species information with system-generated ID."""
    id: str = Field(..., description="Unique identifier for the species")
    
    class Config:
        from_attributes = True
        json_encoders = {
            'HttpUrl': lambda v: str(v) if v else None
        }
        schema_extra = {
            "example": {
                "id": "species-123",
                "scientific_name": "Aedes aegypti",
                "common_name": "Yellow fever mosquito",
                "vector_status": "primary",
                "image_url": "https://example.com/aedes_aegypti.jpg"
            }
        }


class FilterOptionsResponse(BaseModel):
    """Response model for available filter options.
    
    Attributes:
        species: List of available species IDs
        regions: List of available regions
        data_sources: List of available data sources
    """
    species: List[str] = Field(..., description="List of available species IDs")
    regions: List[str] = Field(..., description="List of available regions")
    data_sources: List[str] = Field(..., description="List of available data sources")
    
    class Config:
        schema_extra = {
            "example": {
                "species": ["aedes-aegypti", "anopheles-gambiae"],
                "regions": ["north-america", "europe", "asia"],
                "data_sources": ["who", "cdc", "local"]
            }
        }
