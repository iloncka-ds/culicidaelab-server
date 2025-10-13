# Geographic Data API

The Geographic API handles location-based data and provides endpoints for retrieving geographic information and regional data.

## Router Implementation

::: backend.routers.geo
    options:
      show_root_heading: false
      show_source: true
      members_order: source
      docstring_style: google

## Data Schemas

The Geographic API uses Pydantic schemas for geographic data validation:

::: backend.schemas.geo_schemas
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Service Layer

The Geographic API integrates with geographic service layers:

::: backend.services.geo_service
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Example Usage

### Geographic Data Retrieval

```python
import httpx

async with httpx.AsyncClient() as client:
    # Get regional data
    response = await client.get(
        "http://localhost:8000/api/v1/regions",
        params={"lang": "en"}
    )
    regions = response.json()
    
    # Get country information
    response = await client.get(
        "http://localhost:8000/api/v1/countries",
        params={"lang": "en"}
    )
    countries = response.json()
```