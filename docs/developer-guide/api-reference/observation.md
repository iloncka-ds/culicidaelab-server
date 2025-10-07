# Observation API

The Observation API handles mosquito observation data, including recording new observations and retrieving existing observation records.

## Router Implementation

::: backend.routers.observation
    options:
      show_root_heading: false
      show_source: true
      members_order: source
      docstring_style: google

## Data Schemas

The Observation API uses Pydantic schemas for observation data validation:

::: backend.schemas.observation_schemas
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Service Layer

The Observation API integrates with observation service layers:

::: backend.services.observation_service
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Example Usage

### Create New Observation

```python
import httpx
from datetime import datetime

async with httpx.AsyncClient() as client:
    observation_data = {
        "species_id": "aedes-aegypti",
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060
        },
        "observed_at": datetime.now().isoformat(),
        "observer_name": "Dr. Smith",
        "notes": "Found in urban area near standing water"
    }
    
    response = await client.post(
        "http://localhost:8000/api/v1/observations",
        json=observation_data
    )
    observation = response.json()
    print(f"Created observation ID: {observation['id']}")
```

### Retrieve Observations

```python
# Get list of observations with filters
response = await client.get(
    "http://localhost:8000/api/v1/observations",
    params={
        "species_id": "aedes-aegypti",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "limit": 50
    }
)
observations = response.json()

# Get specific observation details
response = await client.get(
    "http://localhost:8000/api/v1/observations/12345"
)
observation_detail = response.json()
```

### Update Observation

```python
# Update existing observation
update_data = {
    "notes": "Updated notes with additional details",
    "verified": True
}

response = await client.patch(
    "http://localhost:8000/api/v1/observations/12345",
    json=update_data
)
updated_observation = response.json()
```