# Species API

The Species API provides comprehensive endpoints for retrieving mosquito species information, including species lists, detailed species data, and disease vector information.

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/species` | Retrieve paginated list of species with optional search |
| GET | `/species/{species_id}` | Get detailed information for a specific species |
| GET | `/vector-species` | Retrieve species that are disease vectors |

## Router Implementation

::: backend.routers.species
    options:
      show_root_heading: false
      show_source: true
      members_order: source
      docstring_style: google

## Data Schemas

The Species API uses the following Pydantic schemas for request/response validation:

### SpeciesBase Schema

::: backend.schemas.species_schemas.SpeciesBase
    options:
      show_root_heading: true
      show_source: false

### SpeciesDetail Schema

::: backend.schemas.species_schemas.SpeciesDetail
    options:
      show_root_heading: true
      show_source: false

### SpeciesListResponse Schema

::: backend.schemas.species_schemas.SpeciesListResponse
    options:
      show_root_heading: true
      show_source: false

## Service Layer

The Species API integrates with the species service layer for business logic:

::: backend.services.species_service
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Example Usage

### Get Species List

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get(
        "http://localhost:8000/api/v1/species",
        params={"limit": 25, "lang": "en"}
    )
    species_data = response.json()
    print(f"Found {species_data['count']} species")
```

### Search for Species

```python
response = await client.get(
    "http://localhost:8000/api/v1/species",
    params={"search": "aedes", "limit": 10, "lang": "en"}
)
```

### Get Species Details

```python
response = await client.get(
    "http://localhost:8000/api/v1/species/aedes-aegypti",
    params={"lang": "en"}
)
species = response.json()
```

### Get Vector Species

```python
response = await client.get(
    "http://localhost:8000/api/v1/vector-species",
    params={"lang": "en"}
)
vector_species = response.json()
```