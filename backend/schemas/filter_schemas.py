from pydantic import BaseModel, Field


# --- New Nested Models for Filter Options ---
class RegionFilter(BaseModel):
    id: str = Field(..., description="Unique identifier for the region")
    name: str = Field(..., description="Translated name of the region")


class DataSourceFilter(BaseModel):
    id: str = Field(..., description="Unique identifier for the data source")
    name: str = Field(..., description="Translated name of the data source")


# --- Updated FilterOptions Model ---
class FilterOptions(BaseModel):
    species: list[str]
    regions: list[RegionFilter]
    data_sources: list[DataSourceFilter]
