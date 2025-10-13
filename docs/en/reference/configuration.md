# Configuration Reference

This document provides a comprehensive reference for all configuration options available in CulicidaeLab Server, including environment variables, application settings, and deployment configurations.

## Environment Variables

### Backend Configuration

#### Core Application Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CULICIDAELAB_APP_NAME` | string | `"CulicidaeLab API"` | Application name displayed in API documentation |
| `CULICIDAELAB_API_V1_STR` | string | `"/api"` | Base path prefix for API version 1 endpoints |
| `ENVIRONMENT` | string | `"development"` | Application environment (development, staging, production) |

#### Database Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CULICIDAELAB_DATABASE_PATH` | string | `".lancedb"` | File system path to the LanceDB database directory |
| `CULICIDAELAB_DATABASE_TIMEOUT` | integer | `30` | Database connection timeout in seconds |
| `CULICIDAELAB_DATABASE_MAX_CONNECTIONS` | integer | `10` | Maximum number of database connections |

#### Model Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CULICIDAELAB_MODEL_PATH` | string | `"models/"` | Directory path containing model files |
| `CULICIDAELAB_SAVE_PREDICTED_IMAGES` | boolean | `false` | Whether to save predicted images to disk |
| `CULICIDAELAB_PREDICTION_TIMEOUT` | integer | `300` | Timeout for model predictions in seconds |
| `CULICIDAELAB_MAX_IMAGE_SIZE` | integer | `10485760` | Maximum image upload size in bytes (10MB) |

#### Security Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CULICIDAELAB_SECRET_KEY` | string | `""` | Secret key for session management and encryption |
| `CULICIDAELAB_BACKEND_CORS_ORIGINS` | list | `["http://localhost:8765"]` | Allowed CORS origins for frontend access |
| `CULICIDAELAB_ALLOWED_HOSTS` | list | `["localhost", "127.0.0.1"]` | Allowed host headers |
| `CULICIDAELAB_RATE_LIMIT_REQUESTS` | integer | `100` | Number of requests per minute per IP |

#### Logging Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CULICIDAELAB_LOG_LEVEL` | string | `"INFO"` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `CULICIDAELAB_LOG_FILE` | string | `""` | Path to log file (empty for console logging) |
| `CULICIDAELAB_LOG_FORMAT` | string | `"json"` | Log format (json, text) |
| `CULICIDAELAB_LOG_ROTATION` | boolean | `true` | Enable log file rotation |

### Frontend Configuration

#### Application Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `FRONTEND_HOST` | string | `"localhost"` | Host address for frontend server |
| `FRONTEND_PORT` | integer | `8765` | Port number for frontend server |
| `BACKEND_URL` | string | `"http://localhost:8000"` | Backend API base URL |
| `FRONTEND_DEBUG` | boolean | `false` | Enable debug mode for frontend |

#### UI Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `FRONTEND_THEME` | string | `"light"` | Default UI theme (light, dark, auto) |
| `FRONTEND_LANGUAGE` | string | `"en"` | Default language (en, ru) |
| `FRONTEND_MAP_PROVIDER` | string | `"openstreetmap"` | Map tile provider |
| `FRONTEND_MAX_UPLOAD_SIZE` | integer | `52428800` | Maximum file upload size in bytes (50MB) |

## Configuration Files

### Backend Configuration (`backend/config.py`)

The main configuration class `AppSettings` provides centralized access to all application settings:

```python
from backend.config import settings

# Access configuration values
app_name = settings.APP_NAME
database_path = settings.DATABASE_PATH
cors_origins = settings.BACKEND_CORS_ORIGINS

# Access model configuration
model_path = settings.classifier_model_path
predictor_settings = settings.classifier_settings
```

#### Configuration Properties

```python
class AppSettings(BaseSettings):
    # Core settings
    APP_NAME: str = "CulicidaeLab API"
    API_V1_STR: str = "/api"
    DATABASE_PATH: str = ".lancedb"
    SAVE_PREDICTED_IMAGES: str | bool = False
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:8765"]
    
    # Dynamic properties
    @property
    def classifier_settings(self):
        """Returns culicidaelab library settings"""
        
    @property
    def classifier_model_path(self) -> str:
        """Returns path to classifier model weights"""
```

### Environment File (`.env`)

Create a `.env` file in the backend directory for local development:

```bash
# Database configuration
CULICIDAELAB_DATABASE_PATH="backend/data/.lancedb"

# Model configuration
CULICIDAELAB_SAVE_PREDICTED_IMAGES=1
CULICIDAELAB_MODEL_PATH="models/"

# Security
CULICIDAELAB_SECRET_KEY="your-secret-key-here"

# CORS origins (comma-separated)
CULICIDAELAB_BACKEND_CORS_ORIGINS="http://localhost:8765,http://127.0.0.1:8765"

# Logging
CULICIDAELAB_LOG_LEVEL="DEBUG"
CULICIDAELAB_LOG_FILE="logs/culicidaelab.log"

# Environment
ENVIRONMENT="development"
```

### Production Environment File

For production deployments, use more secure settings:

```bash
# Production database path
CULICIDAELAB_DATABASE_PATH="/var/lib/culicidaelab/data/.lancedb"

# Production model path
CULICIDAELAB_MODEL_PATH="/var/lib/culicidaelab/models/"

# Security settings
CULICIDAELAB_SECRET_KEY="your-very-secure-secret-key-here"
CULICIDAELAB_BACKEND_CORS_ORIGINS="https://your-domain.com,https://www.your-domain.com"
CULICIDAELAB_ALLOWED_HOSTS="your-domain.com,www.your-domain.com"

# Performance settings
CULICIDAELAB_DATABASE_MAX_CONNECTIONS=20
CULICIDAELAB_RATE_LIMIT_REQUESTS=1000

# Logging
CULICIDAELAB_LOG_LEVEL="INFO"
CULICIDAELAB_LOG_FILE="/var/log/culicidaelab/app.log"
CULICIDAELAB_LOG_FORMAT="json"

# Environment
ENVIRONMENT="production"
```

## Model Configuration

### CulicidaeLab Library Settings

The application integrates with the `culicidaelab` library for species prediction. Model configuration is managed through the library's settings system:

```python
from backend.config import get_predictor_settings

# Get model settings
settings = get_predictor_settings()

# Access model parameters
confidence_threshold = settings.get_confidence_threshold()
model_weights_path = settings.get_model_weights_path("segmenter")
```

### Model File Structure

```
models/
├── segmenter/
│   ├── weights.pt              # Model weights
│   ├── config.json            # Model configuration
│   └── metadata.json          # Model metadata
├── classifier/
│   ├── weights.pt
│   ├── config.json
│   └── metadata.json
└── preprocessing/
    ├── transforms.json        # Image preprocessing config
    └── normalization.json     # Normalization parameters
```

### Model Configuration Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `confidence_threshold` | float | `0.5` | Minimum confidence for predictions |
| `max_image_size` | tuple | `(1024, 1024)` | Maximum image dimensions |
| `batch_size` | integer | `1` | Batch size for model inference |
| `device` | string | `"auto"` | Device for model inference (cpu, cuda, auto) |
| `preprocessing` | dict | `{}` | Image preprocessing parameters |

## Database Configuration

### LanceDB Settings

CulicidaeLab uses LanceDB for vector storage and similarity search:

```python
# Database connection settings
DATABASE_CONFIG = {
    "path": settings.DATABASE_PATH,
    "timeout": 30,
    "max_connections": 10,
    "vector_dimension": 512,
    "index_type": "IVF_FLAT",
    "metric_type": "L2"
}
```

### Database Schema

The database contains several tables for different data types:

#### Species Table
```python
species_schema = {
    "id": "string",
    "name": "string",
    "scientific_name": "string",
    "vector": "vector(512)",
    "metadata": "json",
    "created_at": "timestamp"
}
```

#### Observations Table
```python
observations_schema = {
    "id": "string",
    "species_id": "string",
    "location": "geometry",
    "confidence": "float",
    "image_path": "string",
    "metadata": "json",
    "created_at": "timestamp"
}
```

## Server Configuration

### FastAPI Settings

```python
# FastAPI application configuration
app = FastAPI(
    title=settings.APP_NAME,
    description="CulicidaeLab API for mosquito species identification",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)
```

### CORS Configuration

```python
# CORS middleware settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### Static Files Configuration

```python
# Static file serving
app.mount("/static", StaticFiles(directory="backend/static"), name="static")
```

## Deployment Configuration

### Docker Configuration

#### Environment Variables for Docker

```yaml
# docker-compose.yml
environment:
  - CULICIDAELAB_DATABASE_PATH=/app/data/.lancedb
  - CULICIDAELAB_MODEL_PATH=/app/models
  - CULICIDAELAB_SAVE_PREDICTED_IMAGES=1
  - CULICIDAELAB_LOG_LEVEL=INFO
  - ENVIRONMENT=production
```

#### Volume Mounts

```yaml
volumes:
  - ./data:/app/data              # Database files
  - ./models:/app/models          # Model files
  - ./logs:/app/logs              # Log files
  - ./uploads:/app/uploads        # User uploads
```

### Nginx Configuration

#### Reverse Proxy Settings

```nginx
# Backend API proxy
location /api {
    proxy_pass http://backend:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Timeout settings for model predictions
    proxy_read_timeout 300s;
    proxy_connect_timeout 75s;
    proxy_send_timeout 300s;
}

# Frontend proxy
location / {
    proxy_pass http://frontend:8765;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # WebSocket support for Solara
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

#### File Upload Settings

```nginx
# Increase upload size limits
client_max_body_size 50M;
client_body_timeout 300s;
client_header_timeout 300s;
```

## Performance Configuration

### Backend Performance

| Setting | Development | Production | Description |
|---------|-------------|------------|-------------|
| Workers | 1 | 4-8 | Number of Uvicorn workers |
| Timeout | 30s | 300s | Request timeout |
| Keep-alive | 2s | 5s | Connection keep-alive |
| Max connections | 10 | 100 | Maximum concurrent connections |

### Frontend Performance

| Setting | Development | Production | Description |
|---------|-------------|------------|-------------|
| Debug mode | True | False | Enable debug features |
| Asset compression | False | True | Compress static assets |
| Caching | Disabled | Enabled | Enable browser caching |

### Database Performance

| Setting | Small | Medium | Large | Description |
|---------|-------|--------|-------|-------------|
| Max connections | 10 | 50 | 100 | Database connection pool size |
| Query timeout | 30s | 60s | 120s | Query execution timeout |
| Cache size | 100MB | 500MB | 1GB | Query result cache size |

## Monitoring Configuration

### Health Check Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Basic health check |
| `/api/health` | GET | API health with database check |
| `/metrics` | GET | Prometheus metrics (if enabled) |

### Logging Configuration

#### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about application flow
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for handled exceptions
- **CRITICAL**: Critical errors that may cause application failure

#### Log Format

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "logger": "culicidaelab.api",
  "message": "Request processed successfully",
  "request_id": "req_123456",
  "user_id": "user_789",
  "duration_ms": 150,
  "status_code": 200
}
```

## Security Configuration

### Authentication Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `SESSION_TIMEOUT` | integer | `3600` | Session timeout in seconds |
| `MAX_LOGIN_ATTEMPTS` | integer | `5` | Maximum failed login attempts |
| `PASSWORD_MIN_LENGTH` | integer | `8` | Minimum password length |
| `REQUIRE_HTTPS` | boolean | `true` | Require HTTPS in production |

### Rate Limiting

```python
# Rate limiting configuration
RATE_LIMITS = {
    "default": "100/minute",
    "prediction": "10/minute",
    "upload": "5/minute",
    "auth": "20/minute"
}
```

### File Upload Security

```python
# Allowed file types and sizes
UPLOAD_CONFIG = {
    "allowed_extensions": [".jpg", ".jpeg", ".png", ".tiff"],
    "max_file_size": 50 * 1024 * 1024,  # 50MB
    "scan_for_malware": True,
    "validate_image_format": True
}
```

## Troubleshooting Configuration Issues

### Common Configuration Problems

1. **Environment Variables Not Loading**
   - Check `.env` file location and syntax
   - Verify environment variable names and prefixes
   - Ensure proper file permissions

2. **Database Connection Issues**
   - Verify database path exists and is writable
   - Check database timeout settings
   - Ensure sufficient disk space

3. **Model Loading Failures**
   - Verify model file paths and permissions
   - Check model file integrity
   - Ensure sufficient memory for model loading

4. **CORS Issues**
   - Verify CORS origins configuration
   - Check protocol (http vs https) matching
   - Ensure proper domain configuration

### Configuration Validation

```python
# Validate configuration on startup
def validate_config():
    """Validate application configuration"""
    errors = []
    
    # Check required environment variables
    required_vars = ["CULICIDAELAB_DATABASE_PATH", "CULICIDAELAB_SECRET_KEY"]
    for var in required_vars:
        if not os.getenv(var):
            errors.append(f"Missing required environment variable: {var}")
    
    # Check file paths
    if not os.path.exists(settings.DATABASE_PATH):
        errors.append(f"Database path does not exist: {settings.DATABASE_PATH}")
    
    # Check model files
    try:
        model_path = settings.classifier_model_path
        if not os.path.exists(model_path):
            errors.append(f"Model file not found: {model_path}")
    except Exception as e:
        errors.append(f"Model configuration error: {e}")
    
    if errors:
        raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
```