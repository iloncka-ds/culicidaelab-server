# Справочник по конфигурации

Этот документ предоставляет исчерпывающий справочник по всем опциям конфигурации, доступным в CulicidaeLab Server, включая переменные окружения, настройки приложения и конфигурации развертывания.

## Переменные окружения

### Конфигурация бэкенда

#### Основные настройки приложения

| Переменная | Тип | По умолчанию | Описание |
|------------|-----|--------------|----------|
| `CULICIDAELAB_APP_NAME` | string | `"CulicidaeLab API"` | Имя приложения, отображаемое в документации API |
| `CULICIDAELAB_API_V1_STR` | string | `"/api"` | Базовый префикс пути для конечных точек API версии 1 |
| `ENVIRONMENT` | string | `"development"` | Среда приложения (development, staging, production) |

#### Конфигурация базы данных

| Переменная | Тип | По умолчанию | Описание |
|------------|-----|--------------|----------|
| `CULICIDAELAB_DATABASE_PATH` | string | `".lancedb"` | Путь файловой системы к директории базы данных LanceDB |
| `CULICIDAELAB_DATABASE_TIMEOUT` | integer | `30` | Таймаут подключения к базе данных в секундах |
| `CULICIDAELAB_DATABASE_MAX_CONNECTIONS` | integer | `10` | Максимальное количество подключений к базе данных |

#### Конфигурация модели

| Переменная | Тип | По умолчанию | Описание |
|------------|-----|--------------|----------|
| `CULICIDAELAB_MODEL_PATH` | string | `"models/"` | Путь к директории, содержащей файлы моделей |
| `CULICIDAELAB_SAVE_PREDICTED_IMAGES` | boolean | `false` | Сохранять ли предсказанные изображения на диск |
| `CULICIDAELAB_PREDICTION_TIMEOUT` | integer | `300` | Таймаут для предсказаний модели в секундах |
| `CULICIDAELAB_MAX_IMAGE_SIZE` | integer | `10485760` | Максимальный размер загружаемого изображения в байтах (10МБ) |

#### Конфигурация безопасности

| Переменная | Тип | По умолчанию | Описание |
|------------|-----|--------------|----------|
| `CULICIDAELAB_SECRET_KEY` | string | `""` | Секретный ключ для управления сессиями и шифрования |
| `CULICIDAELAB_BACKEND_CORS_ORIGINS` | list | `["http://localhost:8765"]` | Разрешенные CORS источники для доступа фронтенда |
| `CULICIDAELAB_ALLOWED_HOSTS` | list | `["localhost", "127.0.0.1"]` | Разрешенные заголовки хостов |
| `CULICIDAELAB_RATE_LIMIT_REQUESTS` | integer | `100` | Количество запросов в минуту на IP |

#### Конфигурация логирования

| Переменная | Тип | По умолчанию | Описание |
|------------|-----|--------------|----------|
| `CULICIDAELAB_LOG_LEVEL` | string | `"INFO"` | Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `CULICIDAELAB_LOG_FILE` | string | `""` | Путь к файлу логов (пустой для логирования в консоль) |
| `CULICIDAELAB_LOG_FORMAT` | string | `"json"` | Формат логов (json, text) |
| `CULICIDAELAB_LOG_ROTATION` | boolean | `true` | Включить ротацию файлов логов |

### Конфигурация фронтенда

#### Настройки приложения

| Переменная | Тип | По умолчанию | Описание |
|------------|-----|--------------|----------|
| `FRONTEND_HOST` | string | `"localhost"` | Адрес хоста для сервера фронтенда |
| `FRONTEND_PORT` | integer | `8765` | Номер порта для сервера фронтенда |
| `BACKEND_URL` | string | `"http://localhost:8000"` | Базовый URL API бэкенда |
| `FRONTEND_DEBUG` | boolean | `false` | Включить режим отладки для фронтенда |

#### Конфигурация UI

| Переменная | Тип | По умолчанию | Описание |
|------------|-----|--------------|----------|
| `FRONTEND_THEME` | string | `"light"` | Тема UI по умолчанию (light, dark, auto) |
| `FRONTEND_LANGUAGE` | string | `"en"` | Язык по умолчанию (en, ru) |
| `FRONTEND_MAP_PROVIDER` | string | `"openstreetmap"` | Провайдер карт |
| `FRONTEND_MAX_UPLOAD_SIZE` | integer | `52428800` | Максимальный размер загружаемого файла в байтах (50МБ) |## Ф
айлы конфигурации

### Конфигурация бэкенда (`backend/config.py`)

Основной класс конфигурации `AppSettings` предоставляет централизованный доступ ко всем настройкам приложения:

```python
from backend.config import settings

# Доступ к значениям конфигурации
app_name = settings.APP_NAME
database_path = settings.DATABASE_PATH
cors_origins = settings.BACKEND_CORS_ORIGINS

# Доступ к конфигурации модели
model_path = settings.classifier_model_path
predictor_settings = settings.classifier_settings
```

#### Свойства конфигурации

```python
class AppSettings(BaseSettings):
    # Основные настройки
    APP_NAME: str = "CulicidaeLab API"
    API_V1_STR: str = "/api"
    DATABASE_PATH: str = ".lancedb"
    SAVE_PREDICTED_IMAGES: str | bool = False
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:8765"]
    
    # Динамические свойства
    @property
    def classifier_settings(self):
        """Возвращает настройки библиотеки culicidaelab"""
        
    @property
    def classifier_model_path(self) -> str:
        """Возвращает путь к весам модели классификатора"""
```

### Файл окружения (`.env`)

Создайте файл `.env` в директории бэкенда для локальной разработки:

```bash
# Конфигурация базы данных
CULICIDAELAB_DATABASE_PATH="backend/data/.lancedb"

# Конфигурация модели
CULICIDAELAB_SAVE_PREDICTED_IMAGES=1
CULICIDAELAB_MODEL_PATH="models/"

# Безопасность
CULICIDAELAB_SECRET_KEY="ваш-секретный-ключ-здесь"

# CORS источники (разделенные запятыми)
CULICIDAELAB_BACKEND_CORS_ORIGINS="http://localhost:8765,http://127.0.0.1:8765"

# Логирование
CULICIDAELAB_LOG_LEVEL="DEBUG"
CULICIDAELAB_LOG_FILE="logs/culicidaelab.log"

# Окружение
ENVIRONMENT="development"
```

### Файл продакшн окружения

Для продакшн развертываний используйте более безопасные настройки:

```bash
# Путь к продакшн базе данных
CULICIDAELAB_DATABASE_PATH="/var/lib/culicidaelab/data/.lancedb"

# Путь к продакшн модели
CULICIDAELAB_MODEL_PATH="/var/lib/culicidaelab/models/"

# Настройки безопасности
CULICIDAELAB_SECRET_KEY="ваш-очень-безопасный-секретный-ключ-здесь"
CULICIDAELAB_BACKEND_CORS_ORIGINS="https://ваш-домен.com,https://www.ваш-домен.com"
CULICIDAELAB_ALLOWED_HOSTS="ваш-домен.com,www.ваш-домен.com"

# Настройки производительности
CULICIDAELAB_DATABASE_MAX_CONNECTIONS=20
CULICIDAELAB_RATE_LIMIT_REQUESTS=1000

# Логирование
CULICIDAELAB_LOG_LEVEL="INFO"
CULICIDAELAB_LOG_FILE="/var/log/culicidaelab/app.log"
CULICIDAELAB_LOG_FORMAT="json"

# Окружение
ENVIRONMENT="production"
```

## Конфигурация модели

### Настройки библиотеки CulicidaeLab

Приложение интегрируется с библиотекой `culicidaelab` для предсказания видов. Конфигурация модели управляется через систему настроек библиотеки:

```python
from backend.config import get_predictor_settings

# Получить настройки модели
settings = get_predictor_settings()

# Доступ к параметрам модели
confidence_threshold = settings.get_confidence_threshold()
model_weights_path = settings.get_model_weights_path("segmenter")
```

### Структура файлов модели

```
models/
├── segmenter/
│   ├── weights.pt              # Веса модели
│   ├── config.json            # Конфигурация модели
│   └── metadata.json          # Метаданные модели
├── classifier/
│   ├── weights.pt
│   ├── config.json
│   └── metadata.json
└── preprocessing/
    ├── transforms.json        # Конфигурация предобработки изображений
    └── normalization.json     # Параметры нормализации
```

### Опции конфигурации модели

| Настройка | Тип | По умолчанию | Описание |
|-----------|-----|--------------|----------|
| `confidence_threshold` | float | `0.5` | Минимальная уверенность для предсказаний |
| `max_image_size` | tuple | `(1024, 1024)` | Максимальные размеры изображения |
| `batch_size` | integer | `1` | Размер пакета для вывода модели |
| `device` | string | `"auto"` | Устройство для вывода модели (cpu, cuda, auto) |
| `preprocessing` | dict | `{}` | Параметры предобработки изображений |

## Конфигурация базы данных

### Настройки LanceDB

CulicidaeLab использует LanceDB для векторного хранения и поиска по сходству:

```python
# Настройки подключения к базе данных
DATABASE_CONFIG = {
    "path": settings.DATABASE_PATH,
    "timeout": 30,
    "max_connections": 10,
    "vector_dimension": 512,
    "index_type": "IVF_FLAT",
    "metric_type": "L2"
}
```

### Схема базы данных

База данных содержит несколько таблиц для разных типов данных:

#### Таблица видов
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

#### Таблица наблюдений
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
```## Ко
нфигурация сервера

### Настройки FastAPI

```python
# Конфигурация приложения FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="CulicidaeLab API для идентификации видов комаров",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)
```

### Конфигурация CORS

```python
# Настройки middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### Конфигурация статических файлов

```python
# Обслуживание статических файлов
app.mount("/static", StaticFiles(directory="backend/static"), name="static")
```

## Конфигурация развертывания

### Конфигурация Docker

#### Переменные окружения для Docker

```yaml
# docker-compose.yml
environment:
  - CULICIDAELAB_DATABASE_PATH=/app/data/.lancedb
  - CULICIDAELAB_MODEL_PATH=/app/models
  - CULICIDAELAB_SAVE_PREDICTED_IMAGES=1
  - CULICIDAELAB_LOG_LEVEL=INFO
  - ENVIRONMENT=production
```

#### Монтирование томов

```yaml
volumes:
  - ./data:/app/data              # Файлы базы данных
  - ./models:/app/models          # Файлы моделей
  - ./logs:/app/logs              # Файлы логов
  - ./uploads:/app/uploads        # Загрузки пользователей
```

### Конфигурация Nginx

#### Настройки обратного прокси

```nginx
# Прокси для API бэкенда
location /api {
    proxy_pass http://backend:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Настройки таймаута для предсказаний модели
    proxy_read_timeout 300s;
    proxy_connect_timeout 75s;
    proxy_send_timeout 300s;
}

# Прокси для фронтенда
location / {
    proxy_pass http://frontend:8765;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Поддержка WebSocket для Solara
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

#### Настройки загрузки файлов

```nginx
# Увеличение лимитов размера загрузки
client_max_body_size 50M;
client_body_timeout 300s;
client_header_timeout 300s;
```

## Конфигурация производительности

### Производительность бэкенда

| Настройка | Разработка | Продакшн | Описание |
|-----------|------------|----------|----------|
| Воркеры | 1 | 4-8 | Количество воркеров Uvicorn |
| Таймаут | 30с | 300с | Таймаут запроса |
| Keep-alive | 2с | 5с | Keep-alive соединения |
| Макс соединений | 10 | 100 | Максимальные одновременные соединения |

### Производительность фронтенда

| Настройка | Разработка | Продакшн | Описание |
|-----------|------------|----------|----------|
| Режим отладки | True | False | Включить функции отладки |
| Сжатие ресурсов | False | True | Сжимать статические ресурсы |
| Кэширование | Отключено | Включено | Включить кэширование браузера |

### Производительность базы данных

| Настройка | Малая | Средняя | Большая | Описание |
|-----------|-------|---------|---------|----------|
| Макс соединений | 10 | 50 | 100 | Размер пула соединений БД |
| Таймаут запроса | 30с | 60с | 120с | Таймаут выполнения запроса |
| Размер кэша | 100МБ | 500МБ | 1ГБ | Размер кэша результатов запросов |

## Конфигурация мониторинга

### Конечные точки проверки здоровья

| Конечная точка | Метод | Описание |
|----------------|-------|----------|
| `/health` | GET | Базовая проверка здоровья |
| `/api/health` | GET | Проверка здоровья API с проверкой БД |
| `/metrics` | GET | Метрики Prometheus (если включены) |

### Конфигурация логирования

#### Уровни логов

- **DEBUG**: Подробная информация для отладки
- **INFO**: Общая информация о потоке приложения
- **WARNING**: Предупреждающие сообщения о потенциальных проблемах
- **ERROR**: Сообщения об ошибках для обработанных исключений
- **CRITICAL**: Критические ошибки, которые могут вызвать сбой приложения

#### Формат логов

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "logger": "culicidaelab.api",
  "message": "Запрос обработан успешно",
  "request_id": "req_123456",
  "user_id": "user_789",
  "duration_ms": 150,
  "status_code": 200
}
```

## Конфигурация безопасности

### Настройки аутентификации

| Настройка | Тип | По умолчанию | Описание |
|-----------|-----|--------------|----------|
| `SESSION_TIMEOUT` | integer | `3600` | Таймаут сессии в секундах |
| `MAX_LOGIN_ATTEMPTS` | integer | `5` | Максимальные неудачные попытки входа |
| `PASSWORD_MIN_LENGTH` | integer | `8` | Минимальная длина пароля |
| `REQUIRE_HTTPS` | boolean | `true` | Требовать HTTPS в продакшне |

### Ограничение скорости

```python
# Конфигурация ограничения скорости
RATE_LIMITS = {
    "default": "100/minute",
    "prediction": "10/minute",
    "upload": "5/minute",
    "auth": "20/minute"
}
```

### Безопасность загрузки файлов

```python
# Разрешенные типы файлов и размеры
UPLOAD_CONFIG = {
    "allowed_extensions": [".jpg", ".jpeg", ".png", ".tiff"],
    "max_file_size": 50 * 1024 * 1024,  # 50МБ
    "scan_for_malware": True,
    "validate_image_format": True
}
```

## Устранение проблем конфигурации

### Общие проблемы конфигурации

1. **Переменные окружения не загружаются**
   - Проверьте расположение и синтаксис файла `.env`
   - Проверьте имена переменных окружения и префиксы
   - Убедитесь в правильных разрешениях файлов

2. **Проблемы подключения к базе данных**
   - Проверьте, что путь к базе данных существует и доступен для записи
   - Проверьте настройки таймаута базы данных
   - Убедитесь в достаточном дисковом пространстве

3. **Сбои загрузки модели**
   - Проверьте пути к файлам модели и разрешения
   - Проверьте целостность файлов модели
   - Убедитесь в достаточной памяти для загрузки модели

4. **Проблемы CORS**
   - Проверьте конфигурацию CORS источников
   - Проверьте соответствие протокола (http vs https)
   - Убедитесь в правильной конфигурации домена

### Валидация конфигурации

```python
# Валидация конфигурации при запуске
def validate_config():
    """Валидация конфигурации приложения"""
    errors = []
    
    # Проверка обязательных переменных окружения
    required_vars = ["CULICIDAELAB_DATABASE_PATH", "CULICIDAELAB_SECRET_KEY"]
    for var in required_vars:
        if not os.getenv(var):
            errors.append(f"Отсутствует обязательная переменная окружения: {var}")
    
    # Проверка путей к файлам
    if not os.path.exists(settings.DATABASE_PATH):
        errors.append(f"Путь к базе данных не существует: {settings.DATABASE_PATH}")
    
    # Проверка файлов модели
    try:
        model_path = settings.classifier_model_path
        if not os.path.exists(model_path):
            errors.append(f"Файл модели не найден: {model_path}")
    except Exception as e:
        errors.append(f"Ошибка конфигурации модели: {e}")
    
    if errors:
        raise ValueError(f"Валидация конфигурации не удалась: {'; '.join(errors)}")
```