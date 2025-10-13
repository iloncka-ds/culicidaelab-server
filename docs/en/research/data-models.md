# Data Models

This document provides comprehensive documentation of the database schema and data structures used in the CulicidaeLab Server platform.

## Overview

CulicidaeLab uses LanceDB as its primary database for storing mosquito research data. The system employs PyArrow schemas to define structured data models that support both vector operations and traditional relational queries.

## Database Architecture

### LanceDB Configuration

The system uses LanceDB, a vector database optimized for AI applications, with the following configuration:

- **Database Path**: Configurable via `CULICIDAELAB_DATABASE_PATH` environment variable (default: `.lancedb`)
- **Schema Definition**: PyArrow schemas for type safety and performance
- **Connection Management**: Async connection pooling with automatic reconnection

### Core Data Models

## Species Data Model

The species table stores comprehensive information about mosquito species, including multilingual support and vector status.

```python
SPECIES_SCHEMA = pa.schema([
    pa.field("id", pa.string(), nullable=False),
    pa.field("scientific_name", pa.string()),
    pa.field("image_url", pa.string()),
    pa.field("vector_status", pa.string()),
    # Localized fields (English/Russian)
    pa.field("common_name_en", pa.string()),
    pa.field("common_name_ru", pa.string()),
    pa.field("description_en", pa.string()),
    pa.field("description_ru", pa.string()),
    pa.field("key_characteristics_en", pa.list_(pa.string())),
    pa.field("key_characteristics_ru", pa.list_(pa.string())),
    pa.field("habitat_preferences_en", pa.list_(pa.string())),
    pa.field("habitat_preferences_ru", pa.list_(pa.string())),
    # Relational fields
    pa.field("geographic_regions", pa.list_(pa.string())),
    pa.field("related_diseases", pa.list_(pa.string())),
    pa.field("related_diseases_info", pa.list_(pa.string())),
])
```

### Key Features:
- **Multilingual Support**: English and Russian localization for all descriptive fields
- **Vector Status**: Classification of disease transmission risk (High, Moderate, Low)
- **Geographic Distribution**: List of regions where species is found
- **Disease Relationships**: Links to diseases transmitted by the species

### Example Species Record:
```json
{
  "id": "aedes_aegypti",
  "scientific_name": "Aedes aegypti",
  "vector_status": "High",
  "common_name_en": "Yellow Fever Mosquito",
  "common_name_ru": "Комар желтой лихорадки",
  "geographic_regions": ["asia", "americas", "africa", "oceania"],
  "related_diseases": ["dengue_fever", "yellow_fever", "chikungunya", "zika_virus"]
}
```

## Disease Data Model

The diseases table contains information about mosquito-borne diseases with multilingual descriptions and vector relationships.

```python
DISEASES_SCHEMA = pa.schema([
    pa.field("id", pa.string(), nullable=False),
    pa.field("image_url", pa.string()),
    # Localized fields
    pa.field("name_en", pa.string()),
    pa.field("name_ru", pa.string()),
    pa.field("description_en", pa.string()),
    pa.field("description_ru", pa.string()),
    pa.field("symptoms_en", pa.string()),
    pa.field("symptoms_ru", pa.string()),
    pa.field("treatment_en", pa.string()),
    pa.field("treatment_ru", pa.string()),
    pa.field("prevention_en", pa.string()),
    pa.field("prevention_ru", pa.string()),
    pa.field("prevalence_en", pa.string()),
    pa.field("prevalence_ru", pa.string()),
    # Vector relationships
    pa.field("vectors", pa.list_(pa.string())),
])
```

### Key Features:
- **Comprehensive Medical Information**: Symptoms, treatment, and prevention in multiple languages
- **Epidemiological Data**: Prevalence and geographic distribution information
- **Vector Mapping**: Links to mosquito species that transmit the disease

## Observation Data Model

The observations table stores field observation data with geospatial information and prediction metadata.

```python
OBSERVATIONS_SCHEMA = pa.schema([
    pa.field("type", pa.string()),
    pa.field("id", pa.string(), nullable=False),
    pa.field("species_scientific_name", pa.string()),
    pa.field("observed_at", pa.string()),
    pa.field("count", pa.int32()),
    pa.field("observer_id", pa.string()),
    pa.field("location_accuracy_m", pa.float32()),
    pa.field("notes", pa.string()),
    pa.field("data_source", pa.string()),
    pa.field("image_filename", pa.string()),
    pa.field("model_id", pa.string()),
    pa.field("confidence", pa.float32()),
    pa.field("geometry_type", pa.string()),
    pa.field("coordinates", pa.list_(pa.float32())),
    pa.field("metadata", pa.string()),
])
```

### Key Features:
- **Geospatial Data**: GeoJSON-compatible coordinate storage
- **AI Integration**: Model predictions with confidence scores
- **Data Provenance**: Source tracking and observer information
- **Flexible Metadata**: JSON storage for additional observation details

## API Schema Models

The system uses Pydantic models for API request/response validation and documentation.

### Observation Models

```python
class Location(BaseModel):
    """Geographic location model."""
    lat: float
    lng: float

class ObservationBase(BaseModel):
    """Base observation data."""
    type: str = "Feature"
    species_scientific_name: str
    count: int = Field(..., gt=0)
    location: Location
    observed_at: str
    notes: str | None = None
    user_id: str | None = None
    location_accuracy_m: int | None = None
    data_source: str | None = None

class Observation(ObservationBase):
    """Complete observation with system fields."""
    id: UUID = Field(default_factory=uuid4)
    image_filename: str | None = None
    model_id: str | None = None
    confidence: float | None = None
    metadata: dict[str, Any] | None = {}
```

### Prediction Models

```python
class PredictionResult(BaseModel):
    """AI model prediction result."""
    id: str
    scientific_name: str
    probabilities: dict[str, float]
    model_id: str
    confidence: float
    image_url_species: str | None = None
```

### Species Models

```python
class SpeciesBase(BaseModel):
    """Base species information."""
    id: str
    scientific_name: str
    common_name: str | None = None
    vector_status: str | None = None
    image_url: str | None = None

class SpeciesDetail(SpeciesBase):
    """Extended species information."""
    description: str | None = None
    key_characteristics: list[str] | None = None
    geographic_regions: list[str] | None = None
    related_diseases: list[str] | None = None
    habitat_preferences: list[str] | None = None
```

## Data Relationships

### Species-Disease Relationships
- **Many-to-Many**: Species can transmit multiple diseases, diseases can be transmitted by multiple species
- **Implementation**: Array fields in both species and disease records
- **Bidirectional**: Relationships maintained in both directions for query efficiency

### Observation-Species Relationships
- **Many-to-One**: Multiple observations can reference the same species
- **Foreign Key**: `species_scientific_name` field links to species table
- **Validation**: API layer ensures species exists before creating observations

### Geographic Relationships
- **Hierarchical**: Regions can contain sub-regions
- **Flexible**: String-based region identifiers allow for various geographic scales
- **Extensible**: New regions can be added without schema changes

## Data Validation and Constraints

### Field Validation
- **Required Fields**: Non-nullable fields enforced at schema level
- **Type Safety**: PyArrow schemas ensure type consistency
- **Range Validation**: Pydantic models provide additional validation (e.g., count > 0)

### Data Integrity
- **UUID Generation**: Automatic unique identifier generation for observations
- **Timestamp Validation**: ISO format datetime strings
- **Coordinate Validation**: Geographic coordinate bounds checking

### Multilingual Consistency
- **Field Pairing**: English and Russian fields maintained together
- **Fallback Logic**: API layer provides fallback to English if localized content missing
- **Validation**: Ensures at least one language version exists for required fields

## Performance Considerations

### Indexing Strategy
- **Primary Keys**: Automatic indexing on ID fields
- **Geographic Queries**: Spatial indexing for coordinate-based searches
- **Text Search**: Full-text indexing on species names and descriptions

### Query Optimization
- **Batch Operations**: Bulk insert/update operations for large datasets
- **Lazy Loading**: Pagination support for large result sets
- **Caching**: Application-level caching for frequently accessed data

### Storage Efficiency
- **Columnar Storage**: LanceDB's columnar format optimizes for analytical queries
- **Compression**: Automatic compression for text and array fields
- **Vector Storage**: Optimized storage for AI model embeddings (future enhancement)