# Конфигурация

Это руководство охватывает параметры конфигурации, доступные для CulicidaeLab Server, включая настройки бэкенд API, конфигурацию фронтенда и настройки для конкретных сред.

## Обзор конфигурации

CulicidaeLab Server использует несколько конфигурационных файлов и переменных окружения для настройки своего поведения:

- **Конфигурация бэкенда:** Переменные окружения и файлы `.env`
- **Конфигурация фронтенда:** Файлы конфигурации Python
- **Конфигурация базы данных:** Настройки и пути LanceDB
- **Конфигурация модели:** Параметры и пути моделей ИИ

## Конфигурация бэкенда

### Переменные окружения

Бэкенд использует переменные окружения для конфигурации. Создайте файл `.env` в директории `backend/`:

```bash
# Скопируйте пример конфигурации
cp backend/.env.example backend/.env
```

### Основные настройки бэкенда

```bash
# Настройки приложения
APP_NAME="CulicidaeLab Server"
APP_VERSION="1.0.0"
DEBUG=false
ENVIRONMENT="production"  # development, staging, production

# Настройки сервера
HOST="0.0.0.0"
PORT=8000
RELOAD=false  # Установите true для разработки

# Настройки базы данных
LANCEDB_PATH="./data/lancedb"
LANCEDB_TABLE_PREFIX="culicidae_"

# Настройки CORS
ALLOWED_ORIGINS=["http://localhost:8765", "https://yourdomain.com"]
ALLOWED_METHODS=["GET", "POST", "PUT", "DELETE"]
ALLOWED_HEADERS=["*"]

# Настройки загрузки файлов
MAX_FILE_SIZE=10485760  # 10MB в байтах
ALLOWED_FILE_TYPES=["image/jpeg", "image/png", "image/jpg"]
UPLOAD_PATH="./uploads"

# Настройки модели ИИ
MODEL_CACHE_DIR="./models"
DEFAULT_CLASSIFICATION_MODEL="culico-net-cls-v1"
DEFAULT_DETECTION_MODEL="culico-net-det-v1"
DEFAULT_SEGMENTATION_MODEL="culico-net-segm-v1-nano"

# Настройки производительности
MAX_WORKERS=4
BATCH_SIZE=1
USE_GPU=true
GPU_MEMORY_FRACTION=0.8

# Настройки логирования
LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE="./logs/culicidaelab.log"
LOG_ROTATION="1 week"
LOG_RETENTION="4 weeks"

# Настройки безопасности
SECRET_KEY="your-secret-key-here"  # Сгенерируйте безопасный случайный ключ
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM="HS256"

# Настройки внешнего API (если применимо)
EXTERNAL_API_KEY=""
EXTERNAL_API_URL=""
API_RATE_LIMIT=100  # запросов в минуту
```

### Структура конфигурационного файла

Конфигурация бэкенда управляется через несколько файлов:

```
backend/
├── config.py              # Основной модуль конфигурации
├── .env                   # Переменные окружения
├── .env.example          # Пример файла окружения
└── dependencies.py       # Конфигурация внедрения зависимостей
```

### Загрузка конфигурации

Конфигурация загружается в `backend/config.py`:

```python
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Настройки приложения
    app_name: str = "CulicidaeLab Server"
    debug: bool = False
    environment: str = "production"
    
    # Настройки сервера
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Настройки базы данных
    lancedb_path: str = "./data/lancedb"
    
    # Настройки модели
    model_cache_dir: str = "./models"
    use_gpu: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

## Конфигурация фронтенда

### Файл настроек фронтенда

Конфигурация фронтенда управляется в `frontend/config.py`:

```python
from typing import Dict, Any, List
import os

class FrontendConfig:
    # Настройки приложения
    APP_TITLE = "CulicidaeLab Server"
    APP_DESCRIPTION = "Платформа исследований и анализа комаров"
    
    # Настройки API
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    API_TIMEOUT = 30  # секунды
    
    # Настройки UI
    THEME = "light"  # light, dark, auto
    DEFAULT_MAP_CENTER = [40.7128, -74.0060]  # Нью-Йорк
    DEFAULT_MAP_ZOOM = 10
    
    # Настройки загрузки файлов
    MAX_FILE_SIZE_MB = 10
    ALLOWED_FILE_EXTENSIONS = [".jpg", ".jpeg", ".png"]
    
    # Настройки карты
    MAP_TILE_URL = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    MAP_ATTRIBUTION = "© OpenStreetMap contributors"
    
    # Настройки производительности
    ENABLE_CACHING = True
    CACHE_TIMEOUT = 300  # 5 минут
    
    # Флаги функций
    ENABLE_SPECIES_PREDICTION = True
    ENABLE_MAP_VISUALIZATION = True
    ENABLE_SPECIES_GALLERY = True
    ENABLE_DISEASE_INFO = True

# Создать глобальный экземпляр конфигурации
config = FrontendConfig()
```

### Настройка поведения фронтенда

Вы можете настроить фронтенд, изменив `frontend/config.py` или установив переменные окружения:

```bash
# Установить базовый URL API
export API_BASE_URL="https://api.yourdomain.com"

# Установить местоположение карты по умолчанию
export DEFAULT_MAP_CENTER="[51.5074, -0.1278]"  # Лондон
export DEFAULT_MAP_ZOOM="12"
```

## Конфигурация базы данных

### Настройки LanceDB

Настройте параметры векторной базы данных:

```python
# В backend/config.py
class DatabaseConfig:
    # Путь к базе данных
    lancedb_path: str = "./data/lancedb"
    
    # Настройки таблиц
    table_prefix: str = "culicidae_"
    
    # Настройки производительности
    max_connections: int = 10
    connection_timeout: int = 30
    
    # Настройки векторов
    vector_dimension: int = 512
    distance_metric: str = "cosine"  # cosine, euclidean, dot
    
    # Настройки индексирования
    index_type: str = "IVF_FLAT"
    nlist: int = 100  # количество кластеров для индекса IVF
```

### Конфигурация примеров данных

Настройте генерацию примеров данных:

```python
# В backend/data/sample_data/config.py
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

## Конфигурация модели

### Настройки модели ИИ

Настройте модели ИИ, используемые для предсказаний:

```python
# Конфигурация модели
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

### Конфигурация GPU

Настройте использование GPU и управление памятью:

```bash
# Настройки GPU
USE_GPU=true
GPU_DEVICE_ID=0  # Использовать конкретное устройство GPU
GPU_MEMORY_FRACTION=0.8  # Использовать 80% памяти GPU
ENABLE_MIXED_PRECISION=true  # Включить FP16 для более быстрого вывода
```

## Конфигурация для конкретных сред

### Среда разработки

```bash
# .env.development
DEBUG=true
ENVIRONMENT="development"
RELOAD=true
LOG_LEVEL="DEBUG"
ALLOWED_ORIGINS=["http://localhost:8765", "http://127.0.0.1:8765"]
```

### Продакшн среда

```bash
# .env.production
DEBUG=false
ENVIRONMENT="production"
RELOAD=false
LOG_LEVEL="INFO"
SECRET_KEY="your-production-secret-key"
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

### Тестовая среда

```bash
# .env.testing
DEBUG=true
ENVIRONMENT="testing"
LANCEDB_PATH="./test_data/lancedb"
LOG_LEVEL="WARNING"
```

## Конфигурация безопасности

### Безопасность API

```bash
# Настройки безопасности
SECRET_KEY="generate-a-secure-random-key"
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM="HS256"

# Настройки CORS
ALLOWED_ORIGINS=["https://yourdomain.com"]
ALLOWED_METHODS=["GET", "POST"]
ALLOWED_HEADERS=["Content-Type", "Authorization"]
```

### Безопасность загрузки файлов

```bash
# Безопасность загрузки файлов
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=["image/jpeg", "image/png"]
SCAN_UPLOADS=true  # Включить сканирование на вирусы, если доступно
QUARANTINE_PATH="./quarantine"
```

## Конфигурация логирования

### Структурированное логирование

Настройте логирование для мониторинга и отладки:

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

## Валидация конфигурации

### Валидация окружения

Проверьте настройки конфигурации при запуске:

```python
def validate_config():
    """Проверить настройки конфигурации"""
    errors = []
    
    # Проверить необходимые директории
    required_dirs = [settings.lancedb_path, settings.model_cache_dir]
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            errors.append(f"Директория не найдена: {dir_path}")
    
    # Проверить доступность GPU
    if settings.use_gpu:
        try:
            import torch
            if not torch.cuda.is_available():
                errors.append("Запрошен GPU, но CUDA недоступна")
        except ImportError:
            errors.append("PyTorch не установлен, но запрошен GPU")
    
    if errors:
        raise ValueError(f"Ошибки конфигурации: {', '.join(errors)}")
```

## Лучшие практики конфигурации

### Лучшие практики безопасности

1. **Никогда не коммитьте файлы `.env`** в систему контроля версий
2. **Используйте сильные секретные ключи** для продакшна
3. **Ограничьте CORS origins** доверенными доменами
4. **Включите HTTPS** в продакшне
5. **Регулярно ротируйте секреты** и API ключи

### Лучшие практики производительности

1. **Настройте размеры батчей** на основе доступной памяти
2. **Настройте соответствующее количество воркеров** для вашего CPU
3. **Используйте ускорение GPU** когда доступно
4. **Установите разумные таймауты** для API вызовов
5. **Включите кэширование** для часто запрашиваемых данных

### Лучшие практики мониторинга

1. **Настройте структурированное логирование** для лучшего анализа
2. **Установите соответствующие уровни логов** для каждой среды
3. **Мониторьте использование ресурсов** и настройте лимиты
4. **Настройте проверки состояния** для критических компонентов
5. **Настройте оповещения** для условий ошибок

## Устранение неполадок конфигурации

### Распространенные проблемы конфигурации

1. **Переменные окружения не загружаются:**
   - Проверьте расположение и синтаксис файла `.env`
   - Убедитесь, что имена переменных окружения соответствуют коду

2. **Проблемы подключения к базе данных:**
   - Проверьте права доступа к пути базы данных
   - Убедитесь в установке LanceDB

3. **Сбои загрузки модели:**
   - Проверьте права доступа к директории кэша модели
   - Убедитесь, что файлы модели загружены

4. **GPU не обнаружен:**
   - Проверьте установку CUDA
   - Убедитесь в драйверах GPU

Для получения дополнительной помощи по устранению неполадок см. [руководство по устранению неполадок](../user-guide/troubleshooting.md).