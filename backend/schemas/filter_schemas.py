"""
Pydantic models for filtering functionality.

This module defines the schema models used for filter options
in API endpoints across different services.
"""

from pydantic import BaseModel, Field


class RegionFilter(BaseModel):
    """Filter model for geographic regions.

    Used to represent available regions for filtering observations and species data.
    """

    id: str = Field(..., description="Unique identifier for the region")
    name: str = Field(..., description="Translated name of the region")


class DataSourceFilter(BaseModel):
    """Filter model for data sources.

    Used to represent available data sources for filtering observations and species data.
    """

    id: str = Field(..., description="Unique identifier for the data source")
    name: str = Field(..., description="Translated name of the data source")


class FilterOptions(BaseModel):
    """Container model for all available filter options.

    Provides comprehensive filtering options including species, regions, and data sources
    for use in API endpoints that support filtering functionality.
    """

    species: list[str]
    regions: list[RegionFilter]
    data_sources: list[DataSourceFilter]
