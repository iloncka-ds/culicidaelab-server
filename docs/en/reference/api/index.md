# API Reference

Complete API reference documentation for the CulicidaeLab Server.

## Quick Start

The CulicidaeLab Server API is a RESTful service built with FastAPI that provides endpoints for mosquito research, surveillance, and data analysis.

### Base URL
```
http://localhost:8000/api/v1
```

### Content Type
All API endpoints accept and return JSON data:
```
Content-Type: application/json
```

## Interactive Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs) - Interactive API explorer
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc) - Alternative documentation format

## OpenAPI Specification

The complete OpenAPI specification is available at:
```
http://localhost:8000/api/v1/openapi.json
```

You can use this specification with any OpenAPI-compatible tool for:
- Code generation
- API testing
- Documentation generation
- Mock server creation

## API Endpoints Summary

### Species Management
- `GET /species` - List mosquito species with search and pagination
- `GET /species/{species_id}` - Get detailed species information
- `GET /vector-species` - List disease vector species

### Disease Information
- `GET /diseases` - List mosquito-borne diseases
- `GET /diseases/{disease_id}` - Get detailed disease information

### Geographic Data
- `GET /regions` - List geographic regions
- `GET /countries` - List countries with mosquito data

### Prediction Services
- `POST /predict` - Predict mosquito species from image
- `POST /predict/batch` - Batch prediction for multiple images

### Observation Management
- `GET /observations` - List mosquito observations
- `POST /observations` - Create new observation
- `GET /observations/{observation_id}` - Get observation details
- `PATCH /observations/{observation_id}` - Update observation

### Data Filtering
- `GET /filters` - Get available filter options
- `GET /filters/{filter_type}` - Get specific filter type options

## Authentication

Currently, the API does not require authentication. Future versions may implement:
- API key authentication
- OAuth2 with JWT tokens
- Role-based access control

## Rate Limiting

No rate limiting is currently implemented. Production deployments should consider:
- Request rate limiting per IP
- API key-based quotas
- Burst protection

## Error Handling

The API uses standard HTTP status codes:

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

### Error Response Format

```json
{
  "detail": "Error description",
  "type": "error_type",
  "errors": [
    {
      "loc": ["field", "name"],
      "msg": "Field validation error",
      "type": "value_error"
    }
  ]
}
```

## Pagination

List endpoints support pagination with query parameters:

- `limit`: Maximum number of results (default: 50, max: 200)
- `offset`: Number of results to skip (default: 0)

### Pagination Response Format

```json
{
  "count": 150,
  "results": [...],
  "next": "http://localhost:8000/api/v1/species?limit=50&offset=50",
  "previous": null
}
```

## Internationalization

The API supports multiple languages through the `lang` query parameter:

- `en`: English (default)
- `es`: Spanish
- `ru`: Russian
- `fr`: French

Example:
```
GET /api/v1/species?lang=es
```

## Data Formats

### Coordinates
Geographic coordinates use decimal degrees:
```json
{
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

### Dates
Dates and timestamps use ISO 8601 format:
```json
{
  "observed_at": "2024-01-15T14:30:00Z",
  "created_at": "2024-01-15T14:30:00.123456Z"
}
```

### Images
Image uploads support:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- Maximum size: 10MB
- Recommended resolution: 224x224 to 1024x1024 pixels

## SDK and Client Libraries

### Python Client Example

```python
import httpx
import asyncio

async def get_species_list():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/species",
            params={"limit": 25, "lang": "en"}
        )
        return response.json()

# Run the example
species_data = asyncio.run(get_species_list())
print(f"Found {species_data['count']} species")
```

### JavaScript/Node.js Client Example

```javascript
const axios = require('axios');

async function getSpeciesList() {
  try {
    const response = await axios.get('http://localhost:8000/api/v1/species', {
      params: {
        limit: 25,
        lang: 'en'
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching species:', error.response.data);
  }
}

// Usage
getSpeciesList().then(data => {
  console.log(`Found ${data.count} species`);
});
```

## Testing the API

### Using curl

```bash
# Get species list
curl -X GET "http://localhost:8000/api/v1/species?limit=10&lang=en"

# Get specific species
curl -X GET "http://localhost:8000/api/v1/species/aedes-aegypti?lang=en"

# Upload image for prediction
curl -X POST "http://localhost:8000/api/v1/predict" \
  -F "image=@mosquito.jpg" \
  -F "confidence_threshold=0.7"
```

### Using HTTPie

```bash
# Get species list
http GET localhost:8000/api/v1/species limit==10 lang==en

# Create observation
http POST localhost:8000/api/v1/observations \
  species_id=aedes-aegypti \
  location:='{"latitude": 40.7128, "longitude": -74.0060}' \
  observer_name="Dr. Smith"
```

## Detailed API Documentation

For detailed documentation of each API endpoint, including request/response schemas and examples, see:

- [Species API](../../developer-guide/api-reference/species.md)
- [Diseases API](../../developer-guide/api-reference/diseases.md)
- [Geographic API](../../developer-guide/api-reference/geo.md)
- [Prediction API](../../developer-guide/api-reference/prediction.md)
- [Observation API](../../developer-guide/api-reference/observation.md)
- [Filters API](../../developer-guide/api-reference/filters.md)
