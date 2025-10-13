# Соображения безопасности

Этот документ описывает комплексные рекомендации по безопасности и лучшие практики для развертывания и поддержания CulicidaeLab Server в production средах.

## Обзор безопасности

CulicidaeLab Server обрабатывает чувствительные исследовательские данные, загрузки пользователей и предоставляет сервисы идентификации видов на основе ИИ. Надежная позиция безопасности необходима для защиты:

- Исследовательских данных и наблюдений
- Загруженных пользователями изображений и метаданных
- API эндпоинтов и сервисов
- Файлов моделей и интеллектуальной собственности
- Системной инфраструктуры и ресурсов

## Аутентификация и авторизация

### Безопасность API

#### Аутентификация по API ключам

Реализация аутентификации по API ключам для программного доступа:

```python
# backend/services/auth.py
import secrets
import hashlib
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

class APIKeyManager:
    """Управление аутентификацией по API ключам"""
    
    def __init__(self):
        self.api_keys = {}  # В production используйте хранение в базе данных
    
    def generate_api_key(self, user_id: str) -> str:
        """Генерация нового API ключа для пользователя"""
        api_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        self.api_keys[key_hash] = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "last_used": None,
            "is_active": True
        }
        
        return api_key
    
    def validate_api_key(self, api_key: str) -> Optional[str]:
        """Валидация API ключа и возврат ID пользователя"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        if key_hash in self.api_keys:
            key_info = self.api_keys[key_hash]
            if key_info["is_active"]:
                key_info["last_used"] = datetime.utcnow()
                return key_info["user_id"]
        
        return None

api_key_manager = APIKeyManager()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Зависимость для получения текущего аутентифицированного пользователя"""
    user_id = api_key_manager.validate_api_key(credentials.credentials)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id

# Использование в эндпоинтах
@app.post("/api/protected-endpoint")
async def protected_endpoint(user_id: str = Depends(get_current_user)):
    return {"message": f"Hello, user {user_id}"}
```

#### Ограничение скорости

Реализация ограничения скорости для предотвращения злоупотреблений:

```python
# backend/services/rate_limiting.py
import time
from collections import defaultdict, deque
from typing import Dict, Deque
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimiter:
    """Ограничитель скорости по алгоритму token bucket"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, Deque[float]] = defaultdict(deque)
    
    def is_allowed(self, identifier: str) -> bool:
        """Проверка разрешения запроса для данного идентификатора"""
        now = time.time()
        minute_ago = now - 60
        
        # Очистка старых запросов
        request_times = self.requests[identifier]
        while request_times and request_times[0] <= minute_ago:
            request_times.popleft()
        
        # Проверка лимита
        if len(request_times) < self.requests_per_minute:
            request_times.append(now)
            return True
        
        return False

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware для ограничения скорости"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.rate_limiter = RateLimiter(requests_per_minute)
    
    async def dispatch(self, request: Request, call_next):
        # Использование IP адреса как идентификатора
        client_ip = request.client.host
        
        if not self.rate_limiter.is_allowed(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
        
        response = await call_next(request)
        return response

# Добавление к FastAPI приложению
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)
```

### Управление сессиями

Реализация безопасной обработки сессий:

```python
# backend/services/sessions.py
import secrets
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class SessionManager:
    """Безопасное управление пользовательскими сессиями"""
    
    def __init__(self, session_timeout: int = 3600):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = session_timeout
    
    def create_session(self, user_id: str, user_data: Dict[str, Any]) -> str:
        """Создание новой сессии"""
        session_id = secrets.token_urlsafe(32)
        
        self.sessions[session_id] = {
            "user_id": user_id,
            "user_data": user_data,
            "created_at": datetime.utcnow(),
            "last_accessed": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(seconds=self.session_timeout)
        }
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Получение данных сессии если валидна"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Проверка истечения сессии
        if datetime.utcnow() > session["expires_at"]:
            del self.sessions[session_id]
            return None
        
        # Обновление времени последнего доступа
        session["last_accessed"] = datetime.utcnow()
        return session
    
    def invalidate_session(self, session_id: str):
        """Аннулирование сессии"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def cleanup_expired_sessions(self):
        """Удаление истекших сессий"""
        now = datetime.utcnow()
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if now > session["expires_at"]
        ]
        
        for sid in expired_sessions:
            del self.sessions[sid]
```

## Валидация и санитизация входных данных

### Безопасность загрузки файлов

Безопасная обработка загрузки файлов:

```python
# backend/services/file_security.py
import os
import magic
import hashlib
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from PIL import Image
import io

class FileValidator:
    """Валидация загруженных файлов для безопасности"""
    
    ALLOWED_MIME_TYPES = [
        'image/jpeg',
        'image/png',
        'image/tiff',
        'image/bmp'
    ]
    
    ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp']
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    def __init__(self):
        self.mime = magic.Magic(mime=True)
    
    def validate_file(self, file: UploadFile) -> bool:
        """Комплексная валидация файла"""
        
        # Проверка размера файла
        if not self._check_file_size(file):
            raise HTTPException(status_code=413, detail="File too large")
        
        # Проверка расширения файла
        if not self._check_extension(file.filename):
            raise HTTPException(status_code=400, detail="Invalid file extension")
        
        # Проверка MIME типа
        file_content = file.file.read()
        file.file.seek(0)  # Сброс указателя файла
        
        if not self._check_mime_type(file_content):
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Валидация формата изображения
        if not self._validate_image_format(file_content):
            raise HTTPException(status_code=400, detail="Invalid or corrupted image")
        
        # Проверка на вредоносное содержимое
        if not self._scan_for_malware(file_content):
            raise HTTPException(status_code=400, detail="File failed security scan")
        
        return True
    
    def _check_file_size(self, file: UploadFile) -> bool:
        """Проверка размера файла в пределах лимитов"""
        file.file.seek(0, 2)  # Переход в конец
        size = file.file.tell()
        file.file.seek(0)  # Сброс в начало
        
        return size <= self.MAX_FILE_SIZE
    
    def _check_extension(self, filename: str) -> bool:
        """Проверка разрешенного расширения файла"""
        if not filename:
            return False
        
        ext = os.path.splitext(filename.lower())[1]
        return ext in self.ALLOWED_EXTENSIONS
    
    def _check_mime_type(self, content: bytes) -> bool:
        """Проверка MIME типа с использованием python-magic"""
        mime_type = self.mime.from_buffer(content)
        return mime_type in self.ALLOWED_MIME_TYPES
    
    def _validate_image_format(self, content: bytes) -> bool:
        """Валидация формата изображения с использованием PIL"""
        try:
            with Image.open(io.BytesIO(content)) as img:
                img.verify()  # Проверка целостности изображения
            return True
        except Exception:
            return False
    
    def _scan_for_malware(self, content: bytes) -> bool:
        """Базовое сканирование на вредоносное ПО (реализовать с ClamAV или аналогом)"""
        # Проверка подозрительных паттернов
        suspicious_patterns = [
            b'<script',
            b'javascript:',
            b'<?php',
            b'<%',
            b'eval(',
            b'exec('
        ]
        
        content_lower = content.lower()
        for pattern in suspicious_patterns:
            if pattern in content_lower:
                return False
        
        return True
    
    def generate_safe_filename(self, original_filename: str) -> str:
        """Генерация безопасного имени файла"""
        # Удаление компонентов пути
        filename = os.path.basename(original_filename)
        
        # Генерация имени файла на основе хеша
        timestamp = str(int(time.time()))
        file_hash = hashlib.md5(filename.encode()).hexdigest()[:8]
        ext = os.path.splitext(filename)[1].lower()
        
        return f"{timestamp}_{file_hash}{ext}"

# Использование в эндпоинтах
file_validator = FileValidator()

@app.post("/api/upload")
async def upload_file(file: UploadFile):
    # Валидация файла
    file_validator.validate_file(file)
    
    # Генерация безопасного имени файла
    safe_filename = file_validator.generate_safe_filename(file.filename)
    
    # Безопасное сохранение файла
    # ... реализация
```

### Санитизация входных данных

Санитизация пользовательских входных данных для предотвращения атак инъекций:

```python
# backend/services/input_sanitization.py
import re
import html
from typing import Any, Dict, List, Union

class InputSanitizer:
    """Санитизация пользовательских входных данных"""
    
    # Regex паттерны для валидации
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    ALPHANUMERIC_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Санитизация строкового входа"""
        if not isinstance(value, str):
            raise ValueError("Input must be a string")
        
        # Обрезка до максимальной длины
        value = value[:max_length]
        
        # HTML экранирование
        value = html.escape(value)
        
        # Удаление null байтов
        value = value.replace('\x00', '')
        
        # Обрезка пробелов
        value = value.strip()
        
        return value
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Валидация формата email"""
        return bool(InputSanitizer.EMAIL_PATTERN.match(email))
    
    @staticmethod
    def validate_alphanumeric(value: str) -> bool:
        """Валидация алфавитно-цифрового входа"""
        return bool(InputSanitizer.ALPHANUMERIC_PATTERN.match(value))
    
    @staticmethod
    def sanitize_coordinates(lat: float, lon: float) -> tuple:
        """Санитизация географических координат"""
        # Валидация диапазона широты
        if not -90 <= lat <= 90:
            raise ValueError("Invalid latitude")
        
        # Валидация диапазона долготы
        if not -180 <= lon <= 180:
            raise ValueError("Invalid longitude")
        
        return round(lat, 6), round(lon, 6)
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any], allowed_keys: List[str]) -> Dict[str, Any]:
        """Санитизация словарного входа"""
        sanitized = {}
        
        for key in allowed_keys:
            if key in data:
                value = data[key]
                
                if isinstance(value, str):
                    sanitized[key] = InputSanitizer.sanitize_string(value)
                elif isinstance(value, (int, float)):
                    sanitized[key] = value
                elif isinstance(value, bool):
                    sanitized[key] = value
                # Добавить больше обработки типов по необходимости
        
        return sanitized

# Pydantic модели с валидацией
from pydantic import BaseModel, validator, Field

class ObservationInput(BaseModel):
    """Валидированная модель входа наблюдения"""
    
    species_name: str = Field(..., max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    confidence: float = Field(..., ge=0, le=1)
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator('species_name')
    def validate_species_name(cls, v):
        return InputSanitizer.sanitize_string(v, 100)
    
    @validator('notes')
    def validate_notes(cls, v):
        if v is not None:
            return InputSanitizer.sanitize_string(v, 1000)
        return v
```

## Защита данных

### Шифрование

#### Данные в покое

Шифрование чувствительных данных, хранящихся в базе данных:

```python
# backend/services/encryption.py
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class DataEncryption:
    """Обработка шифрования и дешифрования данных"""
    
    def __init__(self, password: str):
        self.key = self._derive_key(password)
        self.cipher = Fernet(self.key)
    
    def _derive_key(self, password: str) -> bytes:
        """Вывод ключа шифрования из пароля"""
        salt = os.environ.get('ENCRYPTION_SALT', 'default_salt').encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, data: str) -> str:
        """Шифрование строковых данных"""
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Дешифрование строковых данных"""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = self.cipher.decrypt(encrypted_bytes)
        return decrypted_data.decode()

# Использование для чувствительных полей
encryption = DataEncryption(os.environ.get('ENCRYPTION_PASSWORD'))

class EncryptedObservation:
    """Наблюдение с зашифрованными чувствительными полями"""
    
    def __init__(self, data: dict):
        self.id = data['id']
        self.species_id = data['species_id']
        self.location = data['location']  # Зашифровано
        self.notes = data['notes']  # Зашифровано
        self.created_at = data['created_at']
    
    @classmethod
    def create(cls, species_id: str, location: dict, notes: str):
        """Создание наблюдения с шифрованием"""
        encrypted_location = encryption.encrypt(json.dumps(location))
        encrypted_notes = encryption.encrypt(notes) if notes else None
        
        return cls({
            'id': str(uuid.uuid4()),
            'species_id': species_id,
            'location': encrypted_location,
            'notes': encrypted_notes,
            'created_at': datetime.utcnow()
        })
    
    def get_decrypted_location(self) -> dict:
        """Получение расшифрованных данных местоположения"""
        return json.loads(encryption.decrypt(self.location))
    
    def get_decrypted_notes(self) -> str:
        """Получение расшифрованных заметок"""
        return encryption.decrypt(self.notes) if self.notes else ""
```

#### Данные в передаче

Обеспечение использования HTTPS/TLS для всех коммуникаций:

```nginx
# Конфигурация SSL Nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL сертификаты
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # Настройки безопасности SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # Другие заголовки безопасности
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';";
}
```

### Конфиденциальность данных

#### Соответствие GDPR

Реализация контролей конфиденциальности данных:

```python
# backend/services/privacy.py
from typing import List, Dict, Any
from datetime import datetime, timedelta

class PrivacyManager:
    """Управление конфиденциальностью данных и соответствием GDPR"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Экспорт всех пользовательских данных для соответствия GDPR"""
        user_data = {
            "user_id": user_id,
            "export_date": datetime.utcnow().isoformat(),
            "observations": self._get_user_observations(user_id),
            "uploads": self._get_user_uploads(user_id),
            "sessions": self._get_user_sessions(user_id)
        }
        
        return user_data
    
    def delete_user_data(self, user_id: str) -> bool:
        """Удаление всех пользовательских данных (право на забвение)"""
        try:
            # Удаление наблюдений
            self.db.delete_user_observations(user_id)
            
            # Удаление загруженных файлов
            self._delete_user_files(user_id)
            
            # Удаление сессий
            self.db.delete_user_sessions(user_id)
            
            # Анонимизация оставшихся ссылок
            self._anonymize_user_references(user_id)
            
            return True
        except Exception as e:
            logging.error(f"Failed to delete user data: {e}")
            return False
    
    def anonymize_old_data(self, days_old: int = 365):
        """Анонимизация данных старше указанного количества дней"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Анонимизация старых наблюдений
        old_observations = self.db.get_observations_before(cutoff_date)
        for obs in old_observations:
            self._anonymize_observation(obs)
    
    def _get_user_observations(self, user_id: str) -> List[Dict]:
        """Получение всех наблюдений пользователя"""
        return self.db.get_user_observations(user_id)
    
    def _get_user_uploads(self, user_id: str) -> List[Dict]:
        """Получение всех загрузок файлов пользователя"""
        return self.db.get_user_uploads(user_id)
    
    def _get_user_sessions(self, user_id: str) -> List[Dict]:
        """Получение истории сессий пользователя"""
        return self.db.get_user_sessions(user_id)
    
    def _delete_user_files(self, user_id: str):
        """Удаление всех файлов, загруженных пользователем"""
        user_files = self.db.get_user_files(user_id)
        for file_info in user_files:
            try:
                os.remove(file_info['file_path'])
            except FileNotFoundError:
                pass  # Файл уже удален
    
    def _anonymize_observation(self, observation: Dict):
        """Анонимизация записи наблюдения"""
        # Удаление или хеширование идентифицирующей информации
        observation['user_id'] = 'anonymous'
        observation['ip_address'] = None
        observation['metadata'] = {}
        
        self.db.update_observation(observation)
    
    def _anonymize_user_references(self, user_id: str):
        """Анонимизация ссылок на пользователя в других таблицах"""
        # Обновление любых оставшихся ссылок для использования анонимного ID
        self.db.update_user_references(user_id, 'anonymous')
```

## Безопасность инфраструктуры

### Укрепление сервера

#### Безопасность операционной системы

```bash
#!/bin/bash
# server-hardening.sh

# Обновление системных пакетов
apt update && apt upgrade -y

# Настройка файрвола
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Отключение ненужных сервисов
systemctl disable bluetooth
systemctl disable cups
systemctl disable avahi-daemon

# Настройка безопасности SSH
sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
systemctl restart sshd

# Установка fail2ban
apt install fail2ban -y
systemctl enable fail2ban
systemctl start fail2ban

# Настройка автоматических обновлений безопасности
apt install unattended-upgrades -y
dpkg-reconfigure -plow unattended-upgrades

# Настройка мониторинга логов
apt install logwatch -y
echo "logwatch --output mail --mailto admin@example.com --detail high" > /etc/cron.daily/00logwatch
chmod +x /etc/cron.daily/00logwatch
```

#### Безопасность Docker

```dockerfile
# Практики безопасного Dockerfile
FROM python:3.11-slim

# Создание пользователя без root прав
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Установка обновлений безопасности
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Установка правильных прав доступа
RUN chown -R appuser:appuser /app
USER appuser

# Использование порта без root прав
EXPOSE 8000

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Запуск приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Сетевая безопасность

#### Конфигурация файрвола

```bash
# Правила iptables для дополнительной безопасности
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -j DROP

# Ограничение скорости
iptables -A INPUT -p tcp --dport 80 -m limit --limit 25/minute --limit-burst 100 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -m limit --limit 25/minute --limit-burst 100 -j ACCEPT

# Сохранение правил
iptables-save > /etc/iptables/rules.v4
```

#### VPN доступ

Для административного доступа рассмотрите настройку VPN:

```bash
# Установка WireGuard VPN
apt install wireguard -y

# Генерация ключей сервера
wg genkey | tee /etc/wireguard/private.key
cat /etc/wireguard/private.key | wg pubkey | tee /etc/wireguard/public.key

# Настройка WireGuard
cat > /etc/wireguard/wg0.conf << EOF
[Interface]
PrivateKey = $(cat /etc/wireguard/private.key)
Address = 10.0.0.1/24
ListenPort = 51820
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
PublicKey = CLIENT_PUBLIC_KEY
AllowedIPs = 10.0.0.2/32
EOF

# Включение и запуск WireGuard
systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0
```

## Мониторинг безопасности

### Обнаружение вторжений

#### Конфигурация OSSEC

```xml
<!-- /var/ossec/etc/ossec.conf -->
<ossec_config>
  <global>
    <email_notification>yes</email_notification>
    <smtp_server>localhost</smtp_server>
    <email_from>ossec@culicidaelab.com</email_from>
    <email_to>admin@culicidaelab.com</email_to>
  </global>

  <rules>
    <include>rules_config.xml</include>
    <include>pam_rules.xml</include>
    <include>sshd_rules.xml</include>
    <include>web_rules.xml</include>
    <include>web_appsec_rules.xml</include>
    <include>apache_rules.xml</include>
    <include>nginx_rules.xml</include>
    <include>attack_rules.xml</include>
    <include>local_rules.xml</include>
  </rules>

  <syscheck>
    <directories check_all="yes">/etc,/usr/bin,/usr/sbin</directories>
    <directories check_all="yes">/bin,/sbin</directories>
    <directories check_all="yes">/app</directories>
  </syscheck>

  <rootcheck>
    <rootkit_files>/var/ossec/etc/shared/rootkit_files.txt</rootkit_files>
    <rootkit_trojans>/var/ossec/etc/shared/rootkit_trojans.txt</rootkit_trojans>
  </rootcheck>

  <localfile>
    <log_format>syslog</log_format>
    <location>/var/log/auth.log</location>
  </localfile>

  <localfile>
    <log_format>syslog</log_format>
    <location>/var/log/syslog</location>
  </localfile>

  <localfile>
    <log_format>apache</log_format>
    <location>/var/log/nginx/access.log</location>
  </localfile>

  <localfile>
    <log_format>apache</log_format>
    <location>/var/log/nginx/error.log</location>
  </localfile>
</ossec_config>
```

### Оповещения безопасности

#### Пользовательские оповещения безопасности

```python
# backend/services/security_alerts.py
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

class SecurityAlertManager:
    """Управление оповещениями безопасности и уведомлениями"""
    
    def __init__(self):
        self.failed_attempts = defaultdict(list)
        self.suspicious_activities = []
        
    def log_failed_login(self, ip_address: str, user_agent: str):
        """Логирование неудачной попытки входа"""
        self.failed_attempts[ip_address].append({
            'timestamp': datetime.utcnow(),
            'user_agent': user_agent
        })
        
        # Проверка на атаку перебора
        recent_attempts = [
            attempt for attempt in self.failed_attempts[ip_address]
            if attempt['timestamp'] > datetime.utcnow() - timedelta(minutes=15)
        ]
        
        if len(recent_attempts) >= 5:
            self._trigger_brute_force_alert(ip_address, recent_attempts)
    
    def log_suspicious_activity(self, activity_type: str, details: Dict[str, Any]):
        """Логирование подозрительной активности"""
        alert = {
            'type': activity_type,
            'timestamp': datetime.utcnow(),
            'details': details
        }
        
        self.suspicious_activities.append(alert)
        
        # Отправка немедленного оповещения для критических событий
        if activity_type in ['sql_injection', 'xss_attempt', 'file_upload_malware']:
            self._send_immediate_alert(alert)
    
    def _trigger_brute_force_alert(self, ip_address: str, attempts: List[Dict]):
        """Запуск оповещения о атаке перебора"""
        alert_message = f"Brute force attack detected from IP: {ip_address}"
        logging.critical(alert_message, extra={
            'security_event': 'brute_force',
            'ip_address': ip_address,
            'attempt_count': len(attempts)
        })
        
        # Отправка уведомления администраторам
        self._send_security_notification(alert_message, 'critical')
    
    def _send_immediate_alert(self, alert: Dict[str, Any]):
        """Отправка немедленного оповещения"""
        alert_message = f"Security threat detected: {alert['type']}"
        logging.critical(alert_message, extra={
            'security_event': alert['type'],
            'details': alert['details']
        })
        
        self._send_security_notification(alert_message, 'critical')
    
    def _send_security_notification(self, message: str, severity: str):
        """Отправка уведомления безопасности"""
        # Реализация отправки email/Slack уведомлений
        pass
```

## Лучшие практики безопасности

### Чек-лист безопасности

- [ ] **Аутентификация и авторизация**
  - [ ] API ключи реализованы и защищены
  - [ ] Ограничение скорости настроено
  - [ ] Управление сессиями безопасно
  - [ ] Принцип наименьших привилегий применен

- [ ] **Валидация входных данных**
  - [ ] Все пользовательские входы валидируются
  - [ ] Загрузка файлов безопасно обрабатывается
  - [ ] SQL инъекции предотвращены
  - [ ] XSS атаки предотвращены

- [ ] **Защита данных**
  - [ ] Чувствительные данные зашифрованы в покое
  - [ ] HTTPS/TLS настроен для данных в передаче
  - [ ] Соответствие GDPR реализовано
  - [ ] Регулярные резервные копии создаются

- [ ] **Безопасность инфраструктуры**
  - [ ] Сервер укреплен и обновлен
  - [ ] Файрвол правильно настроен
  - [ ] Ненужные сервисы отключены
  - [ ] Мониторинг и логирование настроены

- [ ] **Мониторинг и реагирование**
  - [ ] Система обнаружения вторжений развернута
  - [ ] Оповещения безопасности настроены
  - [ ] План реагирования на инциденты существует
  - [ ] Регулярные аудиты безопасности проводятся

### Регулярные задачи безопасности

1. **Еженедельно**
   - Обзор логов безопасности
   - Проверка неудачных попыток входа
   - Мониторинг подозрительной активности

2. **Ежемесячно**
   - Обновление системных пакетов
   - Обзор пользовательских доступов
   - Тестирование резервных копий

3. **Ежеквартально**
   - Аудит безопасности
   - Тестирование на проникновение
   - Обновление политик безопасности

4. **Ежегодно**
   - Комплексная оценка безопасности
   - Обновление плана реагирования на инциденты
   - Обучение персонала по безопасности