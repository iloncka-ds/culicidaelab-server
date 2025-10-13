# Развертывание с Docker

Это руководство описывает развертывание CulicidaeLab Server с использованием Docker-контейнеров. Docker обеспечивает согласованную, портативную среду развертывания, которая упрощает настройку и масштабирование.

## Предварительные требования

- Docker Engine 20.10+ установлен
- Docker Compose 2.0+ установлен
- Минимум 4ГБ ОЗУ и 2 ядра процессора
- 10ГБ+ доступного дискового пространства

## Настройка Docker

### 1. Создание Dockerfile для Backend

Создайте `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Установка переменных окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Создание директории приложения
WORKDIR /app

# Установка uv для быстрого управления зависимостями
RUN pip install uv

# Копирование файлов зависимостей
COPY pyproject.toml uv.lock ./
COPY backend/ ./backend/

# Установка Python зависимостей
RUN uv sync --frozen --no-dev

# Создание пользователя без root прав
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Создание директорий для данных
RUN mkdir -p /app/data /app/models /app/logs

# Открытие порта
EXPOSE 8000

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Команда запуска
CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Создание Dockerfile для Frontend

Создайте `frontend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Установка переменных окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Создание директории приложения
WORKDIR /app

# Установка uv для быстрого управления зависимостями
RUN pip install uv

# Копирование файлов зависимостей
COPY pyproject.toml uv.lock ./
COPY frontend/ ./frontend/
COPY backend/config.py ./backend/config.py
COPY backend/__init__.py ./backend/__init__.py

# Установка Python зависимостей
RUN uv sync --frozen --no-dev

# Создание пользователя без root прав
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Открытие порта
EXPOSE 8765

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8765/ || exit 1

# Команда запуска
CMD ["uv", "run", "solara", "run", "frontend.main:routes", "--host", "0.0.0.0", "--port", "8765", "--production"]
```

### 3. Создание многоэтапного Dockerfile (Рекомендуется)

Создайте `Dockerfile` в корне проекта:

```dockerfile
# Многоэтапная сборка для оптимизированного production образа
FROM python:3.11-slim as base

# Установка переменных окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Установка uv
RUN pip install uv

# Этап сборки
FROM base as builder

WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml uv.lock ./

# Установка зависимостей
RUN uv sync --frozen --no-dev

# Production этап
FROM base as production

WORKDIR /app

# Копирование виртуального окружения из builder
COPY --from=builder /app/.venv /app/.venv

# Копирование кода приложения
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Создание пользователя без root прав
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Создание директорий для данных
RUN mkdir -p /app/data /app/models /app/logs

# Backend образ
FROM production as backend
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
CMD ["/app/.venv/bin/uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Frontend образ
FROM production as frontend
EXPOSE 8765
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8765/ || exit 1
CMD ["/app/.venv/bin/solara", "run", "frontend.main:routes", "--host", "0.0.0.0", "--port", "8765", "--production"]
```

## Конфигурация Docker Compose

### 1. Базовый Docker Compose

Создайте `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      target: backend
    ports:
      - "8000:8000"
    environment:
      - CULICIDAELAB_DATABASE_PATH=/app/data/.lancedb
      - CULICIDAELAB_SAVE_PREDICTED_IMAGES=1
      - ENVIRONMENT=production
    volumes:
      - ./data:/app/data
      - ./models:/app/models
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build:
      context: .
      target: frontend
    ports:
      - "8765:8765"
    environment:
      - BACKEND_URL=http://backend:8000
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8765/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  data:
  models:
  logs:
```

### 2. Production Docker Compose

Создайте `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      target: backend
    environment:
      - CULICIDAELAB_DATABASE_PATH=/app/data/.lancedb
      - CULICIDAELAB_SAVE_PREDICTED_IMAGES=1
      - ENVIRONMENT=production
    volumes:
      - data:/app/data
      - models:/app/models
      - logs:/app/logs
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build:
      context: .
      target: frontend
    environment:
      - BACKEND_URL=http://backend:8000
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped
    deploy:
      replicas: 1
      resources:
        limits:
          cpus: '0.5'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8765/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  redis:
    image: redis:alpine
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.25'
          memory: 256M

volumes:
  data:
    driver: local
  models:
    driver: local
  logs:
    driver: local

networks:
  default:
    driver: bridge
```

## Конфигурация Nginx для Docker

Создайте `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:8765;
    }

    server {
        listen 80;
        server_name localhost;

        # Перенаправление HTTP на HTTPS в production
        # return 301 https://$server_name$request_uri;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Поддержка WebSocket
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # Backend API
        location /api {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Увеличение timeout для предсказаний модели
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        # Проверки здоровья
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }

    # HTTPS сервер (раскомментировать для production)
    # server {
    #     listen 443 ssl http2;
    #     server_name your-domain.com;
    #     
    #     ssl_certificate /etc/nginx/ssl/certificate.crt;
    #     ssl_certificate_key /etc/nginx/ssl/private.key;
    #     
    #     # Включить locations сверху
    # }
}
```

## Команды развертывания

### 1. Развертывание для разработки

```bash
# Сборка и запуск сервисов
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d --build

# Просмотр логов
docker-compose logs -f

# Остановка сервисов
docker-compose down
```

### 2. Production развертывание

```bash
# Сборка и запуск production сервисов
docker-compose -f docker-compose.prod.yml up -d --build

# Масштабирование backend сервисов
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Обновление сервисов
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d --no-deps backend frontend

# Просмотр статуса сервисов
docker-compose -f docker-compose.prod.yml ps
```

### 3. Развертывание Docker Swarm

```bash
# Инициализация swarm
docker swarm init

# Развертывание стека
docker stack deploy -c docker-compose.prod.yml culicidaelab

# Масштабирование сервисов
docker service scale culicidaelab_backend=3

# Обновление сервиса
docker service update --image culicidaelab_backend:latest culicidaelab_backend

# Удаление стека
docker stack rm culicidaelab
```

## Переменные окружения

### Переменные окружения Backend

```bash
# Обязательные
CULICIDAELAB_DATABASE_PATH=/app/data/.lancedb
CULICIDAELAB_SAVE_PREDICTED_IMAGES=1
ENVIRONMENT=production

# Опциональные
CULICIDAELAB_MODEL_PATH=/app/models
CULICIDAELAB_LOG_LEVEL=INFO
CULICIDAELAB_WORKERS=4
CULICIDAELAB_BACKEND_CORS_ORIGINS=http://localhost:8765
```

### Переменные окружения Frontend

```bash
# Подключение к backend
BACKEND_URL=http://backend:8000
FRONTEND_PORT=8765
FRONTEND_HOST=0.0.0.0
```

## Постоянство данных

### 1. Управление томами

```bash
# Создание именованных томов
docker volume create culicidaelab_data
docker volume create culicidaelab_models
docker volume create culicidaelab_logs

# Резервное копирование томов
docker run --rm -v culicidaelab_data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz /data

# Восстановление томов
docker run --rm -v culicidaelab_data:/data -v $(pwd):/backup alpine tar xzf /backup/data-backup.tar.gz -C /
```

### 2. Bind Mounts

```yaml
# В docker-compose.yml
volumes:
  - ./data:/app/data              # Файлы базы данных
  - ./models:/app/models          # Файлы моделей
  - ./logs:/app/logs              # Логи приложения
  - ./uploads:/app/uploads        # Загрузки пользователей
```

## Мониторинг и логирование

### 1. Мониторинг контейнеров

```bash
# Мониторинг использования ресурсов
docker stats

# Просмотр логов контейнеров
docker-compose logs -f backend
docker-compose logs -f frontend

# Выполнение команд в контейнерах
docker-compose exec backend bash
docker-compose exec frontend bash
```

### 2. Конфигурация логирования

Создайте `docker-compose.override.yml` для логирования:

```yaml
version: '3.8'

services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  frontend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Лучшие практики безопасности

### 1. Безопасность контейнеров

```dockerfile
# Использование пользователя без root прав
RUN useradd --create-home --shell /bin/bash app
USER app

# Удаление ненужных пакетов
RUN apt-get remove --purge -y build-essential && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Установка правильных прав доступа к файлам
RUN chmod -R 755 /app
```

### 2. Сетевая безопасность

```yaml
# В docker-compose.yml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # Нет внешнего доступа

services:
  backend:
    networks:
      - backend
  frontend:
    networks:
      - frontend
      - backend
```

## Устранение неполадок

### Распространенные проблемы

1. **Контейнер не запускается**
   ```bash
   docker-compose logs backend
   docker-compose logs frontend
   ```

2. **Конфликты портов**
   ```bash
   # Проверка использования портов
   netstat -tulpn | grep :8000
   
   # Использование других портов
   ports:
     - "8001:8000"  # Привязка к другому порту хоста
   ```

3. **Проблемы с правами доступа к томам**
   ```bash
   # Исправление прав доступа
   sudo chown -R 1000:1000 ./data
   sudo chmod -R 755 ./data
   ```

4. **Проблемы с памятью**
   ```bash
   # Увеличение лимитов памяти
   deploy:
     resources:
       limits:
         memory: 4G
   ```

### Оптимизация производительности

1. **Многоэтапные сборки** для уменьшения размера образа
2. **Кэширование слоев** для более быстрых сборок
3. **Лимиты ресурсов** для предотвращения исчерпания ресурсов
4. **Проверки здоровья** для правильной балансировки нагрузки
5. **Ротация логов** для управления использованием диска

## Интеграция CI/CD

### Пример GitHub Actions

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker images
        run: |
          docker build -t culicidaelab-backend --target backend .
          docker build -t culicidaelab-frontend --target frontend .
      
      - name: Deploy to production
        run: |
          docker-compose -f docker-compose.prod.yml up -d
```