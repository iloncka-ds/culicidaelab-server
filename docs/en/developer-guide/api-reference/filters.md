# Filters API

The Filters API provides endpoints for retrieving filter options and managing data filtering capabilities across the CulicidaeLab platform.

## Router Implementation

::: backend.routers.filters
    options:
      show_root_heading: false
      show_source: true
      members_order: source
      docstring_style: google
      heading_level: 3


## Data Schemas

The Filters API uses Pydantic schemas for filter data validation:

::: backend.schemas.filter_schemas
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Service Layer

The Filters API integrates with filter service layers:

::: backend.services.filter_service
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Example Usage

### Get Available Filters

```python
import httpx

async with httpx.AsyncClient() as client:
    # Get all available filter options
    response = await client.get(
        "http://localhost:8000/api/v1/filters",
        params={"lang": "en"}
    )
    filters = response.json()

    print("Available filters:")
    for filter_type, options in filters.items():
        print(f"- {filter_type}: {len(options)} options")
```

### Get Specific Filter Type

```python
# Get species filter options
response = await client.get(
    "http://localhost:8000/api/v1/filters/species",
    params={"lang": "en"}
)
species_filters = response.json()

# Get region filter options
response = await client.get(
    "http://localhost:8000/api/v1/filters/regions",
    params={"lang": "en"}
)
region_filters = response.json()

# Get disease filter options
response = await client.get(
    "http://localhost:8000/api/v1/filters/diseases",
    params={"lang": "en"}
)
disease_filters = response.json()
```

### Apply Filters to Data Queries

```python
# Use filters in species queries
response = await client.get(
    "http://localhost:8000/api/v1/species",
    params={
        "region": "north-america",
        "vector_status": "primary",
        "disease": "malaria",
        "lang": "en"
    }
)
filtered_species = response.json()
```
