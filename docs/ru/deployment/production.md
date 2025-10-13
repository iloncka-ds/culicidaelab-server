# Production развертывание

Это руководство описывает развертывание CulicidaeLab Server в production среде. Приложение состоит из FastAPI backend и Solara frontend, которые могут быть развернуты вместе или отдельно.

## Предварительные требования

Перед развертыванием в production убедитесь, что у вас есть:

- Python 3.11 или выше
- Доступ к серверу с минимум 4ГБ ОЗУ и 2 ядрами процессора
- Доменное имя и SSL сертификат (рекомендуется)
- Хранилище базы данных (локальное или облачное)
- Файлы моделей для предсказания видов

## Архитектура развертывания

CulicidaeLab Server может быть развернут в нескольких конфигурациях:

### Развертывание на одном сервере
- Backend и frontend на одном сервере
- Подходит для малых и средних нагрузок
- Проще в управлении и обслуживании

### Микросервисное развертывание
- Backend и frontend на отдельных серверах
- Лучшая масштабируемость и распределение ресурсов
- Требует настройки балансировщика нагрузки

## Настройка окружения

### 1. Подготовка сервера

```bash
# Обновление системных пакетов
sudo apt update && sudo apt upgrade -y

# Установка Python 3.11+
sudo apt install python3.11 python3.11-venv python3.11-dev

# Установка системных зависимостей
sudo apt install build-essential curl git nginx supervisor
```

### 2. Настройка приложения

```bash
# Клонирование репозитория
git clone https://github.com/your-org/culicidaelab-server.git
cd culicidaelab-server

# Создание виртуального окружения
python3.11 -m venv .venv
source .venv/bin/activate

# Установка зависимостей
pip install uv
uv sync --group production
```

### 3. Конфигурация окружения

Создание production файла окружения:

```bash
# Копирование примера файла окружения
cp backend/.env.example backend/.env

# Редактирование конфигурации для production
nano backend/.env
```

Обязательные переменные окружения для production:

```bash
# Конфигурация базы данных
CULICIDAELAB_DATABASE_PATH="/var/lib/culicidaelab/data/.lancedb"

# Хранение изображений
CULICIDAELAB_SAVE_PREDICTED_IMAGES=1

# Окружение
ENVIRONMENT=production

# Безопасность (генерируйте безопасные значения)
SECRET_KEY="your-secure-secret-key-here"
ALLOWED_HOSTS="your-domain.com,www.your-domain.com"

# CORS origins для frontend
CULICIDAELAB_BACKEND_CORS_ORIGINS="https://your-domain.com,https://www.your-domain.com"
```

## Развертывание приложения

### 1. Развертывание Backend

Создание systemd сервиса для backend:

```bash
sudo nano /etc/systemd/system/culicidaelab-backend.service
```

```ini
[Unit]
Description=CulicidaeLab Backend API
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/culicidaelab-server
Environment=PATH=/path/to/culicidaelab-server/.venv/bin
ExecStart=/path/to/culicidaelab-server/.venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 2. Развертывание Frontend

Создание systemd сервиса для frontend:

```bash
sudo nano /etc/systemd/system/culicidaelab-frontend.service
```

```ini
[Unit]
Description=CulicidaeLab Frontend
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/culicidaelab-server
Environment=PATH=/path/to/culicidaelab-server/.venv/bin
ExecStart=/path/to/culicidaelab-server/.venv/bin/solara run frontend.main:routes --host 127.0.0.1 --port 8765 --production
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 3. Включение и запуск сервисов

```bash
# Включение сервисов
sudo systemctl enable culicidaelab-backend
sudo systemctl enable culicidaelab-frontend

# Запуск сервисов
sudo systemctl start culicidaelab-backend
sudo systemctl start culicidaelab-frontend

# Проверка статуса
sudo systemctl status culicidaelab-backend
sudo systemctl status culicidaelab-frontend
```

## Конфигурация обратного прокси

### Конфигурация Nginx

Создание конфигурации Nginx:

```bash
sudo nano /etc/nginx/sites-available/culicidaelab
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL конфигурация
    ssl_certificate /path/to/ssl/certificate.crt;
    ssl_certificate_key /path/to/ssl/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Заголовки безопасности
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # Frontend (основное приложение)
    location / {
        proxy_pass http://127.0.0.1:8765;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Поддержка WebSocket для Solara
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Увеличение timeout для предсказаний модели
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Статические файлы
    location /static {
        alias /path/to/culicidaelab-server/backend/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Лимит размера загружаемых файлов
    client_max_body_size 50M;
}
```

Включение сайта:

```bash
sudo ln -s /etc/nginx/sites-available/culicidaelab /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Настройка базы данных

### 1. Создание директории базы данных

```bash
sudo mkdir -p /var/lib/culicidaelab/data
sudo chown -R www-data:www-data /var/lib/culicidaelab
sudo chmod 755 /var/lib/culicidaelab
```

### 2. Инициализация базы данных

```bash
# Запуск скрипта инициализации базы данных если доступен
cd /path/to/culicidaelab-server
source .venv/bin/activate
python -m backend.scripts.init_database
```

## Настройка файлов моделей

### 1. Загрузка файлов моделей

```bash
# Создание директории моделей
sudo mkdir -p /var/lib/culicidaelab/models
sudo chown -R www-data:www-data /var/lib/culicidaelab/models

# Загрузка или копирование файлов моделей
# Это зависит от вашего метода распространения моделей
```

### 2. Настройка путей к моделям

Обновление конфигурации окружения для указания на файлы моделей:

```bash
# В backend/.env
CULICIDAELAB_MODEL_PATH="/var/lib/culicidaelab/models"
```

## Проверки здоровья и мониторинг

### 1. Проверки здоровья приложения

Приложение предоставляет эндпоинты проверки здоровья:

- Backend: `https://your-domain.com/api/health`
- Frontend: Мониторинг основного URL приложения

### 2. Мониторинг логов

Настройка ротации и мониторинга логов:

```bash
# Создание директорий логов
sudo mkdir -p /var/log/culicidaelab
sudo chown -R www-data:www-data /var/log/culicidaelab

# Настройка logrotate
sudo nano /etc/logrotate.d/culicidaelab
```

```
/var/log/culicidaelab/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload culicidaelab-backend
        systemctl reload culicidaelab-frontend
    endscript
}
```

## Стратегия резервного копирования

### 1. Резервное копирование базы данных

```bash
#!/bin/bash
# backup-database.sh
BACKUP_DIR="/var/backups/culicidaelab"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/database_$DATE.tar.gz /var/lib/culicidaelab/data/
```

### 2. Резервное копирование приложения

```bash
#!/bin/bash
# backup-application.sh
BACKUP_DIR="/var/backups/culicidaelab"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/application_$DATE.tar.gz /path/to/culicidaelab-server/
```

## Соображения масштабирования

### Горизонтальное масштабирование

Для развертываний с высоким трафиком:

1. **Балансировщик нагрузки**: Использование nginx или HAProxy для распределения трафика
2. **Множественные экземпляры Backend**: Запуск нескольких backend воркеров
3. **Масштабирование базы данных**: Рассмотрение кластеризации или репликации базы данных
4. **CDN**: Использование CDN для статических ресурсов и изображений

### Вертикальное масштабирование

Рекомендации по ресурсам в зависимости от нагрузки:

- **Малая (< 100 пользователей)**: 2 ядра CPU, 4ГБ ОЗУ
- **Средняя (100-1000 пользователей)**: 4 ядра CPU, 8ГБ ОЗУ  
- **Большая (1000+ пользователей)**: 8+ ядер CPU, 16ГБ+ ОЗУ

## Устранение неполадок

### Распространенные проблемы

1. **Сервис не запускается**
   ```bash
   sudo journalctl -u culicidaelab-backend -f
   sudo journalctl -u culicidaelab-frontend -f
   ```

2. **Проблемы с правами доступа**
   ```bash
   sudo chown -R www-data:www-data /path/to/culicidaelab-server
   sudo chmod -R 755 /path/to/culicidaelab-server
   ```

3. **Проблемы подключения к базе данных**
   - Проверка прав доступа к пути базы данных
   - Проверка переменных окружения
   - Проверка дискового пространства

4. **Проблемы загрузки модели**
   - Проверка путей к файлам моделей
   - Проверка прав доступа к файлам моделей
   - Обеспечение достаточной памяти

### Оптимизация производительности

1. **Включение Gzip сжатия** в Nginx
2. **Настройка кэширования** для статических ресурсов
3. **Оптимизация базы данных** запросов и индексирования
4. **Мониторинг использования ресурсов** с помощью инструментов типа htop, iotop

## Чек-лист безопасности

- [ ] SSL/TLS сертификаты настроены
- [ ] Правила файрвола настроены (открыты только порты 80, 443, 22)
- [ ] Регулярные обновления безопасности применяются
- [ ] Сильные пароли и аутентификация по SSH ключам
- [ ] Доступ к базе данных ограничен
- [ ] Логи приложения мониторятся
- [ ] Стратегия резервного копирования реализована
- [ ] Ограничение скорости настроено
- [ ] CORS origins правильно настроены