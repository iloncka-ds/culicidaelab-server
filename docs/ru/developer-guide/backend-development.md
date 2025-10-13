# Руководство по разработке бэкенда

Это руководство охватывает разработку бэкенда для CulicidaeLab Server, включая настройку, архитектурные паттерны и лучшие практики для работы с API сервером на основе FastAPI.

## Настройка среды разработки

### Предварительные требования

- Python 3.11+
- Менеджер пакетов uv (рекомендуется) или pip
- Git
- GPU с поддержкой CUDA (опционально, для ускорения ИИ моделей)

### Первоначальная настройка

1. **Клонирование и переход в проект:**
```bash
git clone https://github.com/iloncka-ds/culicidaelab-server.git
cd culicidaelab-server
```

2. **Настройка Python окружения:**
```bash
# Использование uv (рекомендуется)
uv venv -p 3.11
source .venv/bin/activate  # На Windows: .venv\Scripts\activate
uv sync -p 3.11

# Или использование pip
python -m venv .venv
source .venv/bin/activate  # На Windows: .venv\Scripts\activate
pip install -e .
```

3. **Настройка переменных окружения:**
```bash
# Копирование примера файла окружения
cp backend/.env.example backend/.env

# Редактирование backend/.env с вашими настройками
CULICIDAELAB_DATABASE_PATH=.lancedb
CULICIDAELAB_SAVE_PREDICTED_IMAGES=false
```

4. **Инициализация базы данных:**
```bash
# Генерация примерных данных
python -m backend.data.sample_data.generate_sample_data

# Заполнение LanceDB
python -m backend.scripts.populate_lancedb

# Проверка настройки
python -m backend.scripts.query_lancedb observations --limit 5
```

### Запуск сервера бэкенда

```bash
# Сервер разработки с автоперезагрузкой
uvicorn backend.main:app --port 8000 --host 127.0.0.1 --reload

# Производственный сервер
uvicorn backend.main:app --port 8000 --host 0.0.0.0
```

API будет доступно по адресам:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## Структура проекта

```
backend/
├── main.py                 # Точка входа FastAPI приложения
├── config.py              # Конфигурация приложения
├── dependencies.py        # Внедрение зависимостей
├── routers/               # Обработчики API маршрутов
│   ├── species.py         # Endpoints, связанные с видами
│   ├── diseases.py        # Endpoints информации о болезнях
│   ├── prediction.py      # Endpoints ИИ предсказаний
│   ├── geo.py            # Endpoints географических данных
│   ├── observation.py    # Endpoints пользовательских наблюдений
│   └── filters.py        # Endpoints опций фильтров
├── services/              # Слой бизнес-логики
│   ├── database.py        # Утилиты подключения к базе данных
│   ├── cache_service.py   # Кэширование и загрузка данных
│   ├── species_service.py # Операции с данными видов
│   ├── disease_service.py # Операции с данными болезней
│   ├── prediction_service.py # Логика ИИ предсказаний
│   ├── geo_service.py     # Географические операции
│   └── observation_service.py # Управление наблюдениями
├── schemas/               # Pydantic модели данных
│   ├── species_schemas.py # Структуры данных видов
│   ├── diseases_schemas.py # Структуры данных болезней
│   ├── prediction_schemas.py # Запрос/ответ предсказаний
│   ├── geo_schemas.py     # Структуры географических данных
│   └── observation_schemas.py # Структуры данных наблюдений
├── database_utils/        # Утилиты базы данных
│   └── lancedb_manager.py # Операции LanceDB
├── scripts/               # Утилитарные скрипты
│   ├── populate_lancedb.py # Инициализация базы данных
│   └── query_lancedb.py   # Инструменты запросов к базе данных
└── static/                # Обслуживание статических файлов
    └── images/            # Ресурсы изображений
```

## Архитектурные паттерны

### Слоистая архитектура

Бэкенд следует чистой слоистой архитектуре:

1. **Слой роутеров**: Обработка HTTP запросов и форматирование ответов
2. **Слой сервисов**: Бизнес-логика и обработка данных
3. **Слой схем**: Валидация и сериализация данных
4. **Слой данных**: Операции с базой данных и вызовы внешних API

### Внедрение зависимостей

Система внедрения зависимостей FastAPI используется повсеместно:

```python
# dependencies.py
from fastapi import Depends
from backend.services.database import get_db

def get_database_connection():
    return get_db()

# В роутерах
@router.get("/species")
async def get_species(db=Depends(get_database_connection)):
    # Использование соединения с БД
    pass
```

### Управление конфигурацией

Настройки управляются с использованием Pydantic BaseSettings:

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

## Руководящие принципы разработки API

### Структура роутера

Каждый роутер должен следовать этому паттерну:

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
    """Получить список примеров.
    
    Args:
        limit: Максимальное количество результатов для возврата
        service: Внедренная зависимость сервиса
        
    Returns:
        Список объектов примеров
        
    Raises:
        HTTPException: Если примеры не могут быть получены
    """
    try:
        return await service.get_examples(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Определение схем

Используйте Pydantic модели для всех схем запросов/ответов:

```python
# schemas/example_schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ExampleBase(BaseModel):
    """Базовая схема для объектов примеров."""
    name: str = Field(..., description="Название примера")
    description: Optional[str] = Field(None, description="Опциональное описание")

class ExampleCreate(ExampleBase):
    """Схема для создания новых примеров."""
    pass

class ExampleResponse(ExampleBase):
    """Схема для ответов API примеров."""
    id: str = Field(..., description="Уникальный идентификатор")
    created_at: datetime = Field(..., description="Временная метка создания")
    
    model_config = {"from_attributes": True}
```

### Реализация слоя сервисов

Сервисы содержат бизнес-логику:

```python
# services/example_service.py
from typing import List
from backend.services.database import get_db, get_table
from backend.schemas.example_schemas import ExampleResponse

class ExampleService:
    """Сервис для операций, связанных с примерами."""
    
    def __init__(self):
        self.db = get_db()
        self.table = get_table(self.db, "examples")
    
    async def get_examples(self, limit: int = 10) -> List[ExampleResponse]:
        """Получить примеры из базы данных.
        
        Args:
            limit: Максимальное количество результатов
            
        Returns:
            Список объектов примеров
        """
        try:
            results = self.table.search().limit(limit).to_list()
            return [ExampleResponse(**item) for item in results]
        except Exception as e:
            raise ValueError(f"Не удалось получить примеры: {e}")
```

## Операции с базой данных

### Интеграция LanceDB

Система использует LanceDB для векторного поиска по сходству и хранения данных:

```python
# Работа с LanceDB
from backend.services.database import get_db, get_table

# Получение соединения с базой данных
db = get_db()

# Открытие таблицы
species_table = get_table(db, "species")

# Базовые запросы
results = species_table.search().limit(10).to_list()

# Векторный поиск по сходству
query_vector = [0.1, 0.2, 0.3, ...]  # Ваш вектор встраивания
similar_species = (
    species_table
    .search(query_vector)
    .limit(5)
    .to_list()
)

# Фильтрованные запросы
filtered_results = (
    species_table
    .search()
    .where("region = 'Europe'")
    .limit(10)
    .to_list()
)
```

### Управление схемой базы данных

Таблицы создаются и управляются через скрипты:

```python
# scripts/populate_lancedb.py
import lancedb
import pandas as pd

def create_species_table(db):
    """Создать и заполнить таблицу видов."""
    # Загрузка данных
    df = pd.read_json("sample_data/sample_species.json")
    
    # Создание таблицы со схемой
    table = db.create_table("species", df, mode="overwrite")
    
    # Создание индексов для производительности
    table.create_index("scientific_name")
    table.create_index("region")
    
    return table
```

## Интеграция ИИ/МО

### Сервис предсказаний

Сервис предсказаний интегрируется с библиотекой culicidaelab:

```python
# services/prediction_service.py
from culicidaelab import get_predictor
from backend.config import settings

class PredictionService:
    """Сервис для предсказания видов с помощью ИИ."""
    
    def __init__(self):
        self.predictor = get_predictor(settings.classifier_settings)
    
    async def predict_species(self, image_path: str) -> dict:
        """Предсказать вид комара по изображению.
        
        Args:
            image_path: Путь к файлу изображения
            
        Returns:
            Результаты предсказания с оценками уверенности
        """
        try:
            results = self.predictor.predict(image_path)
            return {
                "species": results.species,
                "confidence": results.confidence,
                "alternatives": results.alternatives
            }
        except Exception as e:
            raise ValueError(f"Предсказание не удалось: {e}")
```

### Управление моделями

Модели управляются через систему конфигурации:

```python
# config.py
def get_predictor_model_path():
    """Получить путь к модели предиктора."""
    settings = get_settings()
    return settings.get_model_weights_path("segmenter")

def get_predictor_settings():
    """Получить полную конфигурацию предиктора."""
    return get_settings()
```

## Обработка ошибок

### Стратегия обработки исключений

Используйте согласованные паттерны обработки ошибок:

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
                detail=f"Вид {species_id} не найден"
            )
        return species
    except ValueError as e:
        logger.error(f"Ошибка валидации: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
```

### Пользовательские классы исключений

Определите исключения, специфичные для домена:

```python
# exceptions.py
class CulicidaeLabException(Exception):
    """Базовое исключение для ошибок CulicidaeLab."""
    pass

class SpeciesNotFoundError(CulicidaeLabException):
    """Возникает, когда вид не может быть найден."""
    pass

class PredictionError(CulicidaeLabException):
    """Возникает, когда ИИ предсказание не удается."""
    pass
```

## Тестирование

### Модульное тестирование

Пишите всесторонние модульные тесты:

```python
# tests/test_species_service.py
import pytest
from backend.services.species_service import SpeciesService

@pytest.fixture
def species_service():
    return SpeciesService()

@pytest.mark.asyncio
async def test_get_species_by_id(species_service):
    """Тест получения вида по ID."""
    species = await species_service.get_by_id("aedes_aegypti")
    assert species is not None
    assert species.scientific_name == "Aedes aegypti"

@pytest.mark.asyncio
async def test_get_nonexistent_species(species_service):
    """Тест обработки несуществующего вида."""
    with pytest.raises(SpeciesNotFoundError):
        await species_service.get_by_id("nonexistent_species")
```

### Интеграционное тестирование

Тестирование API endpoints:

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_get_species_list():
    """Тест endpoint списка видов."""
    response = client.get("/api/species")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_predict_species():
    """Тест endpoint предсказания видов."""
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

## Оптимизация производительности

### Стратегия кэширования

Реализуйте кэширование для часто запрашиваемых данных:

```python
# services/cache_service.py
from functools import lru_cache
from typing import Dict, List

@lru_cache(maxsize=128)
def load_species_names(db_conn) -> Dict[str, str]:
    """Кэшировать названия видов для быстрого поиска."""
    table = get_table(db_conn, "species")
    results = table.search().to_list()
    return {item["id"]: item["scientific_name"] for item in results}

# Кэширование при запуске приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Загрузка кэшей при запуске
    app.state.SPECIES_NAMES = load_species_names(get_db())
    yield
```

### Оптимизация базы данных

Оптимизируйте запросы к базе данных:

```python
# Эффективные паттерны запросов
def get_species_with_pagination(offset: int, limit: int):
    """Получить виды с эффективной пагинацией."""
    return (
        species_table
        .search()
        .offset(offset)
        .limit(limit)
        .select(["id", "scientific_name", "common_names"])  # Выбрать только нужные поля
        .to_list()
    )

# Использование индексов для фильтрации
def search_species_by_region(region: str):
    """Поиск видов по региону с использованием индекса."""
    return (
        species_table
        .search()
        .where(f"region = '{region}'")  # Использует индекс региона
        .to_list()
    )
```

## Лучшие практики безопасности

### Валидация входных данных

Всегда валидируйте входные данные с использованием Pydantic:

```python
from pydantic import BaseModel, validator
from typing import Optional

class SpeciesQuery(BaseModel):
    region: Optional[str] = None
    limit: int = 10
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Лимит должен быть между 1 и 100')
        return v
    
    @validator('region')
    def validate_region(cls, v):
        if v and len(v) < 2:
            raise ValueError('Регион должен содержать минимум 2 символа')
        return v
```

### Безопасность загрузки файлов

Безопасная обработка файлов для загрузки изображений:

```python
from fastapi import UploadFile, HTTPException
import magic

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def validate_image_upload(file: UploadFile):
    """Валидировать загруженный файл изображения."""
    # Проверка размера файла
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "Файл слишком большой")
    
    # Проверка MIME типа
    mime_type = magic.from_buffer(content, mime=True)
    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, "Недопустимый тип файла")
    
    # Сброс указателя файла
    await file.seek(0)
    return file
```

## Соображения развертывания

### Конфигурация окружения

Используйте настройки, специфичные для окружения:

```python
# config.py
class AppSettings(BaseSettings):
    # Настройки разработки vs производства
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Настройки базы данных
    DATABASE_PATH: str = ".lancedb"
    DATABASE_BACKUP_ENABLED: bool = True
    
    # Настройки безопасности
    CORS_ORIGINS: List[str] = ["http://localhost:8765"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CULICIDAELAB_"
    )
```

### Проверки состояния

Реализуйте endpoints проверки состояния:

```python
@app.get("/health")
async def health_check():
    """Endpoint проверки состояния для мониторинга."""
    try:
        # Проверка подключения к базе данных
        db = get_db()
        db.table_names()  # Простой тест подключения
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(500, f"Проверка состояния не удалась: {e}")
```

### Конфигурация логирования

Настройте структурированное логирование:

```python
import logging
import sys

def setup_logging():
    """Настроить логирование приложения."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log')
        ]
    )
    
    # Установить специфичные уровни логов
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
```

Это руководство предоставляет основу для разработки бэкенда на CulicidaeLab Server. Для конкретных деталей реализации обращайтесь к существующей кодовой базе и API документации, доступной по адресу `/docs` при запуске сервера.