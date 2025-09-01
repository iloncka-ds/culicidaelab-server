from pydantic import BaseModel


class SpeciesBase(BaseModel):
    id: str
    scientific_name: str
    common_name: str | None = None
    vector_status: str | None = None
    image_url: str | None = None


class SpeciesDetail(SpeciesBase):
    description: str | None = None
    key_characteristics: list[str] | None = None
    geographic_regions: list[str] | None = None
    related_diseases: list[str] | None = None
    habitat_preferences: list[str] | None = None


class SpeciesListResponse(BaseModel):
    count: int
    species: list[SpeciesBase]
