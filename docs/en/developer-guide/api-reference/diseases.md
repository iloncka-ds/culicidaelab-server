# Diseases API

The Diseases API manages disease-related data and provides endpoints for retrieving information about mosquito-borne diseases.

## Router Implementation

::: backend.routers.diseases
    options:
      show_root_heading: false
      show_source: true
      members_order: source
      docstring_style: google

## Data Schemas

The Diseases API uses Pydantic schemas for request/response validation:

::: backend.schemas.diseases_schemas
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Service Layer

The Diseases API integrates with the disease service layer:

::: backend.services.disease_service
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Example Usage

### Basic Disease Information Retrieval

```python
import httpx

async with httpx.AsyncClient() as client:
    # Get list of diseases
    response = await client.get(
        "http://localhost:8000/api/v1/diseases",
        params={"lang": "en"}
    )
    diseases = response.json()
    
    # Get specific disease details
    response = await client.get(
        "http://localhost:8000/api/v1/diseases/malaria",
        params={"lang": "en"}
    )
    disease_detail = response.json()
```