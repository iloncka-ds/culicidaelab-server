from pydantic import BaseModel, Field
from typing import List


# --- New Nested Models for Filter Options ---
class RegionFilter(BaseModel):
    id: str = Field(..., description="Unique identifier for the region")
    name: str = Field(..., description="Translated name of the region")


class DataSourceFilter(BaseModel):
    id: str = Field(..., description="Unique identifier for the data source")
    name: str = Field(..., description="Translated name of the data source")


# --- Updated FilterOptions Model ---
class FilterOptions(BaseModel):
    species: List[str]
    regions: List[RegionFilter]
    data_sources: List[DataSourceFilter]

