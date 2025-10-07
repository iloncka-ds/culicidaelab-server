---
tags:
  - api
  - reference
  - development
  - backend
  - fastapi
---

# API Reference

Comprehensive API documentation for CulicidaeLab Server backend services.

## Overview

The CulicidaeLab Server provides a RESTful API built with FastAPI for mosquito research, surveillance, and data analysis. The API offers endpoints for species identification, disease tracking, geographic data management, and observation recording.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API does not require authentication for most endpoints. Future versions may implement API key or OAuth2 authentication.

## Response Format

All API responses follow a consistent JSON format with appropriate HTTP status codes:

- `200 OK`: Successful request
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

## Interactive API Documentation

For interactive API exploration, visit the automatically generated documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Modules

### Core Application

::: backend.main
    options:
      show_root_heading: true
      show_source: false
      members_order: source
      
### Species Management

The Species API provides endpoints for retrieving mosquito species information, including detailed species data and disease vector information.

::: backend.routers.species
    options:
      show_root_heading: true
      show_source: false
      members_order: source

### Disease Information

The Diseases API manages disease-related data and provides endpoints for retrieving information about mosquito-borne diseases.

::: backend.routers.diseases
    options:
      show_root_heading: true
      show_source: false
      members_order: source

### Geographic Data

The Geographic API handles location-based data and provides endpoints for retrieving geographic information and regional data.

::: backend.routers.geo
    options:
      show_root_heading: true
      show_source: false
      members_order: source

### Prediction Services

The Prediction API provides machine learning-based species identification and prediction services.

::: backend.routers.prediction
    options:
      show_root_heading: true
      show_source: false
      members_order: source

### Observation Management

The Observation API handles mosquito observation data, including recording and retrieving observation records.

::: backend.routers.observation
    options:
      show_root_heading: true
      show_source: false
      members_order: source

### Data Filtering

The Filters API provides endpoints for retrieving filter options and managing data filtering capabilities.

::: backend.routers.filters
    options:
      show_root_heading: true
      show_source: false
      members_order: source