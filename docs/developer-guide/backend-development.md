# Backend Development Guide

This guide covers backend development for the CulicidaeLab Server, including setup, architecture patterns, and best practices for working with the FastAPI-based API server.

## Development Environment Setup

### Prerequisites

- Python 3.11+
- uv package manager (recommended) or pip
- Git
- CUDA-capable GPU (optional, for AI model acceleration)

### Initial Setup

1. **Clone and navigate to the project:**
```bash
git clone https://github.com/iloncka-ds/culicidaelab-server.git
cd culicidaelab-server
```

2. **Set up Python environment:**
```bash
# Using uv (recommended)
uv venv -p 3.11
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync -p 3.11

# Or using pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

3. **Configure environment variables:**
```bash
# Copy example environment file
cp backend/.env.example backend/.env

# Edit backend/.env with your settings
CULICIDAELAB_DATABASE_PATH=.lancedb
CULICIDAELAB_SAVE_PREDICTED_IMAGES=false
```

4. **Initialize the database:**
```bash
# Generate sample data
python -m backend.data.sample_data.generate_sample_data

# Populate LanceDB
python -m backend.scripts.populate_lancedb

# Verify setup
python -m backend.scripts.query_lancedb observations --limit 5
```

### Running the Backend Server

```bash
# Development server with auto-reload
uvicorn backend.main:app --port 8000 --host 127.0.0.1 --reload

# Production server
uvicorn backend.main:app --port 8000 --host 0.0.0.0
```

The API will be available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py              # Application configuration
├── dependencies.py        # Dependency injection
├── routers/               # API route handlers
│   ├── species.py         # Species-related endpoints
│   ├── diseases.py        # Disease information endpoints
│   ├── prediction.py      # AI prediction endpoints
│   ├── geo.py            # Geographic data endpoints
│   ├── observation.py    # User observation endpoints
│   └── filters.py        # Filter options endpoints
├── services/              # Business logic layer
│   ├── database.py        # Database connection utilities
│   ├── cache_service.py   # Caching and data loading
│   ├── species_service.py # Species data operations
│   ├── disease_service.py # Disease data operations
│   ├── prediction_service.py # AI prediction logic
│   ├── geo_service.py     # Geographic operations
│   └── observation_service.py # Observation management
├── schemas/               # Pydantic data models
│   ├── species_schemas.py # Species data structures
│   ├── diseases_schemas.py # Disease data structures
│   ├── prediction_schemas.py # Prediction request/response
│   ├── geo_schemas.py     # Geographic data structures
│   └── observation_schemas.py # Observation data structures
├── database_utils/        # Database utilities
│   └── lancedb_manager.py # LanceDB operations
├── scripts/               # Utility scripts
│   ├── populate_lancedb.py # Database initialization
│   └── query_lancedb.py   # Database querying tools
└── static/                # Static file serving
    └── images/            # Image assets
```

## Architecture Patterns

### Layered Architecture

The backend follows a clean layered architecture:

1. **Router Layer**: HTTP request handling and response formatting
2. **Service Layer**: Business logic and data processing
3. **Schema Layer**: Data validation and serialization
4. **Data Layer**: Database operations and external API calls

### Dependency Injection

FastAPI's dependency injection system is used throughout:

```python
# dependencies.py
from fastapi import Depends
from backend.services.database import get_db

def get_database_connection():
    return get_db()

# In routers
@router.get("/species")
async def get_species(db=Depends(get_database_connection)):
    # Use db connection
    pass
```

### Configuration Management

Settings are managed using Pydantic BaseSettings:

```python
# config.py
from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    APP_NAME: str = "CulicidaeLab API"
    DATABASE_PATH: str = ".lancedb"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CULICIDAELAB_"
    )

settings = AppSettings()
```

## API Development Guidelines

### Router Structure

Each router should follow this pattern:

```python
# routers/example.py
from fastapi import APIRouter, Depends, HTTPException
from backend.schemas.example_schemas import ExampleResponse
from backend.services.example_service import ExampleService

router = APIRouter()

@router.get("/examples", response_model=list[ExampleResponse])
async def get_examples(
    limit: int = 10,
    service: ExampleService = Depends()
):
    """Get a list of examples.
    
    Args:
        limit: Maximum number of results to return
        service: Injected service dependency
        
    Returns:
        List of example objects
        
    Raises:
        HTTPException: If examples cannot be retrieved
    """
    try:
        return await service.get_examples(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Schema Definition

Use Pydantic models for all request/response schemas:

```python
# schemas/example_schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ExampleBase(BaseModel):
    """Base schema for example objects."""
    name: str = Field(..., description="Example name")
    description: Optional[str] = Field(None, description="Optional description")

class ExampleCreate(ExampleBase):
    """Schema for creating new examples."""
    pass

class ExampleResponse(ExampleBase):
    """Schema for example API responses."""
    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    model_config = {"from_attributes": True}
```

### Service Layer Implementation

Services contain the business logic:

```python
# services/example_service.py
from typing import List
from backend.services.database import get_db, get_table
from backend.schemas.example_schemas import ExampleResponse

class ExampleService:
    """Service for example-related operations."""
    
    def __init__(self):
        self.db = get_db()
        self.table = get_table(self.db, "examples")
    
    async def get_examples(self, limit: int = 10) -> List[ExampleResponse]:
        """Retrieve examples from the database.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of example objects
        """
        try:
            results = self.table.search().limit(limit).to_list()
            return [ExampleResponse(**item) for item in results]
        except Exception as e:
            raise ValueError(f"Failed to retrieve examples: {e}")
```

## Database Operations

### LanceDB Integration

The system uses LanceDB for vector similarity search and data storage:

```python
# Working with LanceDB
from backend.services.database import get_db, get_table

# Get database connection
db = get_db()

# Open a table
species_table = get_table(db, "species")

# Basic queries
results = species_table.search().limit(10).to_list()

# Vector similarity search
query_vector = [0.1, 0.2, 0.3, ...]  # Your embedding vector
similar_species = (
    species_table
    .search(query_vector)
    .limit(5)
    .to_list()
)

# Filtered queries
filtered_results = (
    species_table
    .search()
    .where("region = 'Europe'")
    .limit(10)
    .to_list()
)
```

### Database Schema Management

Tables are created and managed through scripts:

```python
# scripts/populate_lancedb.py
import lancedb
import pandas as pd

def create_species_table(db):
    """Create and populate species table."""
    # Load data
    df = pd.read_json("sample_data/sample_species.json")
    
    # Create table with schema
    table = db.create_table("species", df, mode="overwrite")
    
    # Create indexes for performance
    table.create_index("scientific_name")
    table.create_index("region")
    
    return table
```

## AI/ML Integration

### Prediction Service

The prediction service integrates with the culicidaelab library:

```python
# services/prediction_service.py
from culicidaelab import get_predictor
from backend.config import settings

class PredictionService:
    """Service for AI-powered species prediction."""
    
    def __init__(self):
        self.predictor = get_predictor(settings.classifier_settings)
    
    async def predict_species(self, image_path: str) -> dict:
        """Predict mosquito species from image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Prediction results with confidence scores
        """
        try:
            results = self.predictor.predict(image_path)
            return {
                "species": results.species,
                "confidence": results.confidence,
                "alternatives": results.alternatives
            }
        except Exception as e:
            raise ValueError(f"Prediction failed: {e}")
```

### Model Management

Models are managed through the configuration system:

```python
# config.py
def get_predictor_model_path():
    """Get the path to the predictor model."""
    settings = get_settings()
    return settings.get_model_weights_path("segmenter")

def get_predictor_settings():
    """Get complete predictor configuration."""
    return get_settings()
```

## Error Handling

### Exception Handling Strategy

Use consistent error handling patterns:

```python
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

@router.get("/species/{species_id}")
async def get_species(species_id: str):
    try:
        species = await species_service.get_by_id(species_id)
        if not species:
            raise HTTPException(
                status_code=404, 
                detail=f"Species {species_id} not found"
            )
        return species
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Custom Exception Classes

Define domain-specific exceptions:

```python
# exceptions.py
class CulicidaeLabException(Exception):
    """Base exception for CulicidaeLab errors."""
    pass

class SpeciesNotFoundError(CulicidaeLabException):
    """Raised when a species cannot be found."""
    pass

class PredictionError(CulicidaeLabException):
    """Raised when AI prediction fails."""
    pass
```

## Testing

### Unit Testing

Write comprehensive unit tests:

```python
# tests/test_species_service.py
import pytest
from backend.services.species_service import SpeciesService

@pytest.fixture
def species_service():
    return SpeciesService()

@pytest.mark.asyncio
async def test_get_species_by_id(species_service):
    """Test retrieving species by ID."""
    species = await species_service.get_by_id("aedes_aegypti")
    assert species is not None
    assert species.scientific_name == "Aedes aegypti"

@pytest.mark.asyncio
async def test_get_nonexistent_species(species_service):
    """Test handling of nonexistent species."""
    with pytest.raises(SpeciesNotFoundError):
        await species_service.get_by_id("nonexistent_species")
```

### Integration Testing

Test API endpoints:

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_get_species_list():
    """Test species list endpoint."""
    response = client.get("/api/species")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_predict_species():
    """Test species prediction endpoint."""
    with open("test_image.jpg", "rb") as f:
        response = client.post(
            "/api/predict_species/",
            files={"file": ("test.jpg", f, "image/jpeg")}
        )
    assert response.status_code == 200
    data = response.json()
    assert "species" in data
    assert "confidence" in data
```

## Performance Optimization

### Caching Strategy

Implement caching for frequently accessed data:

```python
# services/cache_service.py
from functools import lru_cache
from typing import Dict, List

@lru_cache(maxsize=128)
def load_species_names(db_conn) -> Dict[str, str]:
    """Cache species names for quick lookup."""
    table = get_table(db_conn, "species")
    results = table.search().to_list()
    return {item["id"]: item["scientific_name"] for item in results}

# Application startup caching
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load caches on startup
    app.state.SPECIES_NAMES = load_species_names(get_db())
    yield
```

### Database Optimization

Optimize database queries:

```python
# Efficient querying patterns
def get_species_with_pagination(offset: int, limit: int):
    """Get species with efficient pagination."""
    return (
        species_table
        .search()
        .offset(offset)
        .limit(limit)
        .select(["id", "scientific_name", "common_names"])  # Select only needed fields
        .to_list()
    )

# Use indexes for filtering
def search_species_by_region(region: str):
    """Search species by region using index."""
    return (
        species_table
        .search()
        .where(f"region = '{region}'")  # Uses region index
        .to_list()
    )
```

## Security Best Practices

### Input Validation

Always validate inputs using Pydantic:

```python
from pydantic import BaseModel, validator
from typing import Optional

class SpeciesQuery(BaseModel):
    region: Optional[str] = None
    limit: int = 10
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Limit must be between 1 and 100')
        return v
    
    @validator('region')
    def validate_region(cls, v):
        if v and len(v) < 2:
            raise ValueError('Region must be at least 2 characters')
        return v
```

### File Upload Security

Secure file handling for image uploads:

```python
from fastapi import UploadFile, HTTPException
import magic

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def validate_image_upload(file: UploadFile):
    """Validate uploaded image file."""
    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large")
    
    # Check MIME type
    mime_type = magic.from_buffer(content, mime=True)
    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, "Invalid file type")
    
    # Reset file pointer
    await file.seek(0)
    return file
```

## Deployment Considerations

### Environment Configuration

Use environment-specific settings:

```python
# config.py
class AppSettings(BaseSettings):
    # Development vs Production settings
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Database settings
    DATABASE_PATH: str = ".lancedb"
    DATABASE_BACKUP_ENABLED: bool = True
    
    # Security settings
    CORS_ORIGINS: List[str] = ["http://localhost:8765"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CULICIDAELAB_"
    )
```

### Health Checks

Implement health check endpoints:

```python
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check database connectivity
        db = get_db()
        db.table_names()  # Simple connectivity test
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(500, f"Health check failed: {e}")
```

### Logging Configuration

Set up structured logging:

```python
import logging
import sys

def setup_logging():
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log')
        ]
    )
    
    # Set specific log levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
```

This guide provides the foundation for backend development on the CulicidaeLab Server. For specific implementation details, refer to the existing codebase and the API documentation available at `/docs` when running the server.