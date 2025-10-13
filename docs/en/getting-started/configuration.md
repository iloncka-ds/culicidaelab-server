# Configuration

This guide covers the configuration options available for CulicidaeLab Server, including backend API settings, frontend configuration, and environment-specific customizations.

## Configuration Overview

CulicidaeLab Server uses multiple configuration files and environment variables to customize its behavior:

- **Backend Configuration:** Environment variables and `.env` files
- **Frontend Configuration:** Python configuration files
- **Database Configuration:** LanceDB settings and paths
- **Model Configuration:** AI model parameters and paths

## Backend Configuration

### Environment Variables

The backend uses environment variables for configuration. Create a `.env` file in the `backend/` directory:

```bash
# Copy the example configuration
cp backend/.env.example backend/.env
```

### Core Backend Settings

```bash
# Application Settings
APP_NAME="CulicidaeLab Server"
APP_VERSION="1.0.0"
DEBUG=false
ENVIRONMENT="production"  # development, staging, production

# Server Settings
HOST="0.0.0.0"
PORT=8000
RELOAD=false  # Set to true for development

# Database Settings
LANCEDB_PATH="./data/lancedb"
LANCEDB_TABLE_PREFIX="culicidae_"

# CORS Settings
ALLOWED_ORIGINS=["http://localhost:8765", "https://yourdomain.com"]
ALLOWED_METHODS=["GET", "POST", "PUT", "DELETE"]
ALLOWED_HEADERS=["*"]

# File Upload Settings
MAX_FILE_SIZE=10485760  # 10MB in bytes
ALLOWED_FILE_TYPES=["image/jpeg", "image/png", "image/jpg"]
UPLOAD_PATH="./uploads"

# AI Model Settings
MODEL_CACHE_DIR="./models"
DEFAULT_CLASSIFICATION_MODEL="culico-net-cls-v1"
DEFAULT_DETECTION_MODEL="culico-net-det-v1"
DEFAULT_SEGMENTATION_MODEL="culico-net-segm-v1-nano"

# Performance Settings
MAX_WORKERS=4
BATCH_SIZE=1
USE_GPU=true
GPU_MEMORY_FRACTION=0.8

# Logging Settings
LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE="./logs/culicidaelab.log"
LOG_ROTATION="1 week"
LOG_RETENTION="4 weeks"

# Security Settings
SECRET_KEY="your-secret-key-here"  # Generate a secure random key
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM="HS256"

# External API Settings (if applicable)
EXTERNAL_API_KEY=""
EXTERNAL_API_URL=""
API_RATE_LIMIT=100  # requests per minute
```

### Configuration File Structure

The backend configuration is managed through several files:

```
backend/
├── config.py              # Main configuration module
├── .env                   # Environment variables
├── .env.example          # Example environment file
└── dependencies.py       # Dependency injection configuration
```

### Loading Configuration

The configuration is loaded in `backend/config.py`:

```python
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Application settings
    app_name: str = "CulicidaeLab Server"
    debug: bool = False
    environment: str = "production"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database settings
    lancedb_path: str = "./data/lancedb"
    
    # Model settings
    model_cache_dir: str = "./models"
    use_gpu: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

## Frontend Configuration

### Frontend Settings File

The frontend configuration is managed in `frontend/config.py`:

```python
from typing import Dict, Any, List
import os

class FrontendConfig:
    # Application settings
    APP_TITLE = "CulicidaeLab Server"
    APP_DESCRIPTION = "Mosquito Research & Analysis Platform"
    
    # API settings
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    API_TIMEOUT = 30  # seconds
    
    # UI settings
    THEME = "light"  # light, dark, auto
    DEFAULT_MAP_CENTER = [40.7128, -74.0060]  # New York City
    DEFAULT_MAP_ZOOM = 10
    
    # File upload settings
    MAX_FILE_SIZE_MB = 10
    ALLOWED_FILE_EXTENSIONS = [".jpg", ".jpeg", ".png"]
    
    # Map settings
    MAP_TILE_URL = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    MAP_ATTRIBUTION = "© OpenStreetMap contributors"
    
    # Performance settings
    ENABLE_CACHING = True
    CACHE_TIMEOUT = 300  # 5 minutes
    
    # Feature flags
    ENABLE_SPECIES_PREDICTION = True
    ENABLE_MAP_VISUALIZATION = True
    ENABLE_SPECIES_GALLERY = True
    ENABLE_DISEASE_INFO = True

# Create global config instance
config = FrontendConfig()
```

### Customizing Frontend Behavior

You can customize the frontend by modifying `frontend/config.py` or setting environment variables:

```bash
# Set API base URL
export API_BASE_URL="https://api.yourdomain.com"

# Set default map location
export DEFAULT_MAP_CENTER="[51.5074, -0.1278]"  # London
export DEFAULT_MAP_ZOOM="12"
```

## Database Configuration

### LanceDB Settings

Configure the vector database settings:

```python
# In backend/config.py
class DatabaseConfig:
    # Database path
    lancedb_path: str = "./data/lancedb"
    
    # Table settings
    table_prefix: str = "culicidae_"
    
    # Performance settings
    max_connections: int = 10
    connection_timeout: int = 30
    
    # Vector settings
    vector_dimension: int = 512
    distance_metric: str = "cosine"  # cosine, euclidean, dot
    
    # Indexing settings
    index_type: str = "IVF_FLAT"
    nlist: int = 100  # number of clusters for IVF index
```

### Sample Data Configuration

Configure sample data generation:

```python
# In backend/data/sample_data/config.py
SAMPLE_DATA_CONFIG = {
    "species_count": 46,
    "observations_per_species": 10,
    "diseases_count": 20,
    "geographic_bounds": {
        "min_lat": -90,
        "max_lat": 90,
        "min_lon": -180,
        "max_lon": 180
    }
}
```

## Model Configuration

### AI Model Settings

Configure the AI models used for predictions:

```python
# Model configuration
MODEL_CONFIG = {
    "classification": {
        "model_name": "culico-net-cls-v1",
        "model_path": "./models/classification/",
        "input_size": (224, 224),
        "batch_size": 1,
        "confidence_threshold": 0.5
    },
    "detection": {
        "model_name": "culico-net-det-v1",
        "model_path": "./models/detection/",
        "input_size": (640, 640),
        "batch_size": 1,
        "confidence_threshold": 0.25,
        "iou_threshold": 0.45
    },
    "segmentation": {
        "model_name": "culico-net-segm-v1-nano",
        "model_path": "./models/segmentation/",
        "input_size": (512, 512),
        "batch_size": 1,
        "confidence_threshold": 0.3
    }
}
```

### GPU Configuration

Configure GPU usage and memory management:

```bash
# GPU settings
USE_GPU=true
GPU_DEVICE_ID=0  # Use specific GPU device
GPU_MEMORY_FRACTION=0.8  # Use 80% of GPU memory
ENABLE_MIXED_PRECISION=true  # Enable FP16 for faster inference
```

## Environment-Specific Configuration

### Development Environment

```bash
# .env.development
DEBUG=true
ENVIRONMENT="development"
RELOAD=true
LOG_LEVEL="DEBUG"
ALLOWED_ORIGINS=["http://localhost:8765", "http://127.0.0.1:8765"]
```

### Production Environment

```bash
# .env.production
DEBUG=false
ENVIRONMENT="production"
RELOAD=false
LOG_LEVEL="INFO"
SECRET_KEY="your-production-secret-key"
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

### Testing Environment

```bash
# .env.testing
DEBUG=true
ENVIRONMENT="testing"
LANCEDB_PATH="./test_data/lancedb"
LOG_LEVEL="WARNING"
```

## Security Configuration

### API Security

```bash
# Security settings
SECRET_KEY="generate-a-secure-random-key"
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM="HS256"

# CORS settings
ALLOWED_ORIGINS=["https://yourdomain.com"]
ALLOWED_METHODS=["GET", "POST"]
ALLOWED_HEADERS=["Content-Type", "Authorization"]
```

### File Upload Security

```bash
# File upload security
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=["image/jpeg", "image/png"]
SCAN_UPLOADS=true  # Enable virus scanning if available
QUARANTINE_PATH="./quarantine"
```

## Logging Configuration

### Structured Logging

Configure logging for monitoring and debugging:

```python
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "./logs/culicidaelab.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "detailed",
            "level": "DEBUG"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    }
}
```

## Configuration Validation

### Environment Validation

Validate configuration on startup:

```python
def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Check required directories
    required_dirs = [settings.lancedb_path, settings.model_cache_dir]
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            errors.append(f"Directory not found: {dir_path}")
    
    # Check GPU availability
    if settings.use_gpu:
        try:
            import torch
            if not torch.cuda.is_available():
                errors.append("GPU requested but CUDA not available")
        except ImportError:
            errors.append("PyTorch not installed but GPU requested")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
```

## Configuration Best Practices

### Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use strong secret keys** for production
3. **Limit CORS origins** to trusted domains
4. **Enable HTTPS** in production
5. **Regularly rotate secrets** and API keys

### Performance Best Practices

1. **Tune batch sizes** based on available memory
2. **Configure appropriate worker counts** for your CPU
3. **Use GPU acceleration** when available
4. **Set reasonable timeouts** for API calls
5. **Enable caching** for frequently accessed data

### Monitoring Best Practices

1. **Configure structured logging** for better analysis
2. **Set appropriate log levels** for each environment
3. **Monitor resource usage** and adjust limits
4. **Set up health checks** for critical components
5. **Configure alerting** for error conditions

## Troubleshooting Configuration

### Common Configuration Issues

1. **Environment variables not loaded:**
   - Check `.env` file location and syntax
   - Verify environment variable names match code

2. **Database connection issues:**
   - Check database path permissions
   - Verify LanceDB installation

3. **Model loading failures:**
   - Check model cache directory permissions
   - Verify model files are downloaded

4. **GPU not detected:**
   - Check CUDA installation
   - Verify GPU drivers

For more troubleshooting help, see the [troubleshooting guide](../user-guide/troubleshooting.md).