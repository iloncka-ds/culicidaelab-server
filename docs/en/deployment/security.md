# Security Considerations

This document outlines comprehensive security guidelines and best practices for deploying and maintaining CulicidaeLab Server in production environments.

## Security Overview

CulicidaeLab Server handles sensitive research data, user uploads, and provides AI-powered species identification services. A robust security posture is essential to protect:

- Research data and observations
- User-uploaded images and metadata
- API endpoints and services
- Model files and intellectual property
- System infrastructure and resources

## Authentication and Authorization

### API Security

#### API Key Authentication

Implement API key authentication for programmatic access:

```python
# backend/services/auth.py
import secrets
import hashlib
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

class APIKeyManager:
    """Manage API key authentication"""
    
    def __init__(self):
        self.api_keys = {}  # In production, use database storage
    
    def generate_api_key(self, user_id: str) -> str:
        """Generate a new API key for a user"""
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
        """Validate API key and return user ID"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        if key_hash in self.api_keys:
            key_info = self.api_keys[key_hash]
            if key_info["is_active"]:
                key_info["last_used"] = datetime.utcnow()
                return key_info["user_id"]
        
        return None

api_key_manager = APIKeyManager()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user"""
    user_id = api_key_manager.validate_api_key(credentials.credentials)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id

# Usage in endpoints
@app.post("/api/protected-endpoint")
async def protected_endpoint(user_id: str = Depends(get_current_user)):
    return {"message": f"Hello, user {user_id}"}
```

#### Rate Limiting

Implement rate limiting to prevent abuse:

```python
# backend/services/rate_limiting.py
import time
from collections import defaultdict, deque
from typing import Dict, Deque
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, Deque[float]] = defaultdict(deque)
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for given identifier"""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        request_times = self.requests[identifier]
        while request_times and request_times[0] <= minute_ago:
            request_times.popleft()
        
        # Check if under limit
        if len(request_times) < self.requests_per_minute:
            request_times.append(now)
            return True
        
        return False

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.rate_limiter = RateLimiter(requests_per_minute)
    
    async def dispatch(self, request: Request, call_next):
        # Use IP address as identifier
        client_ip = request.client.host
        
        if not self.rate_limiter.is_allowed(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
        
        response = await call_next(request)
        return response

# Add to FastAPI app
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)
```

### Session Management

Implement secure session handling:

```python
# backend/services/sessions.py
import secrets
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class SessionManager:
    """Manage user sessions securely"""
    
    def __init__(self, session_timeout: int = 3600):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = session_timeout
    
    def create_session(self, user_id: str, user_data: Dict[str, Any]) -> str:
        """Create a new session"""
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
        """Get session data if valid"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session expired
        if datetime.utcnow() > session["expires_at"]:
            del self.sessions[session_id]
            return None
        
        # Update last accessed time
        session["last_accessed"] = datetime.utcnow()
        return session
    
    def invalidate_session(self, session_id: str):
        """Invalidate a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        now = datetime.utcnow()
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if now > session["expires_at"]
        ]
        
        for sid in expired_sessions:
            del self.sessions[sid]
```

## Input Validation and Sanitization

### File Upload Security

Secure file upload handling:

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
    """Validate uploaded files for security"""
    
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
        """Comprehensive file validation"""
        
        # Check file size
        if not self._check_file_size(file):
            raise HTTPException(status_code=413, detail="File too large")
        
        # Check file extension
        if not self._check_extension(file.filename):
            raise HTTPException(status_code=400, detail="Invalid file extension")
        
        # Check MIME type
        file_content = file.file.read()
        file.file.seek(0)  # Reset file pointer
        
        if not self._check_mime_type(file_content):
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Validate image format
        if not self._validate_image_format(file_content):
            raise HTTPException(status_code=400, detail="Invalid or corrupted image")
        
        # Check for malicious content
        if not self._scan_for_malware(file_content):
            raise HTTPException(status_code=400, detail="File failed security scan")
        
        return True
    
    def _check_file_size(self, file: UploadFile) -> bool:
        """Check if file size is within limits"""
        file.file.seek(0, 2)  # Seek to end
        size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        return size <= self.MAX_FILE_SIZE
    
    def _check_extension(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        if not filename:
            return False
        
        ext = os.path.splitext(filename.lower())[1]
        return ext in self.ALLOWED_EXTENSIONS
    
    def _check_mime_type(self, content: bytes) -> bool:
        """Check MIME type using python-magic"""
        mime_type = self.mime.from_buffer(content)
        return mime_type in self.ALLOWED_MIME_TYPES
    
    def _validate_image_format(self, content: bytes) -> bool:
        """Validate image format using PIL"""
        try:
            with Image.open(io.BytesIO(content)) as img:
                img.verify()  # Verify image integrity
            return True
        except Exception:
            return False
    
    def _scan_for_malware(self, content: bytes) -> bool:
        """Basic malware scanning (implement with ClamAV or similar)"""
        # Check for suspicious patterns
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
        """Generate a safe filename"""
        # Remove path components
        filename = os.path.basename(original_filename)
        
        # Generate hash-based filename
        timestamp = str(int(time.time()))
        file_hash = hashlib.md5(filename.encode()).hexdigest()[:8]
        ext = os.path.splitext(filename)[1].lower()
        
        return f"{timestamp}_{file_hash}{ext}"

# Usage in endpoints
file_validator = FileValidator()

@app.post("/api/upload")
async def upload_file(file: UploadFile):
    # Validate file
    file_validator.validate_file(file)
    
    # Generate safe filename
    safe_filename = file_validator.generate_safe_filename(file.filename)
    
    # Save file securely
    # ... implementation
```

### Input Sanitization

Sanitize user inputs to prevent injection attacks:

```python
# backend/services/input_sanitization.py
import re
import html
from typing import Any, Dict, List, Union

class InputSanitizer:
    """Sanitize user inputs"""
    
    # Regex patterns for validation
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    ALPHANUMERIC_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            raise ValueError("Input must be a string")
        
        # Truncate to max length
        value = value[:max_length]
        
        # HTML escape
        value = html.escape(value)
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Strip whitespace
        value = value.strip()
        
        return value
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        return bool(InputSanitizer.EMAIL_PATTERN.match(email))
    
    @staticmethod
    def validate_alphanumeric(value: str) -> bool:
        """Validate alphanumeric input"""
        return bool(InputSanitizer.ALPHANUMERIC_PATTERN.match(value))
    
    @staticmethod
    def sanitize_coordinates(lat: float, lon: float) -> tuple:
        """Sanitize geographic coordinates"""
        # Validate latitude range
        if not -90 <= lat <= 90:
            raise ValueError("Invalid latitude")
        
        # Validate longitude range
        if not -180 <= lon <= 180:
            raise ValueError("Invalid longitude")
        
        return round(lat, 6), round(lon, 6)
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any], allowed_keys: List[str]) -> Dict[str, Any]:
        """Sanitize dictionary input"""
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
                # Add more type handling as needed
        
        return sanitized

# Pydantic models with validation
from pydantic import BaseModel, validator, Field

class ObservationInput(BaseModel):
    """Validated observation input model"""
    
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

## Data Protection

### Encryption

#### Data at Rest

Encrypt sensitive data stored in the database:

```python
# backend/services/encryption.py
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class DataEncryption:
    """Handle data encryption and decryption"""
    
    def __init__(self, password: str):
        self.key = self._derive_key(password)
        self.cipher = Fernet(self.key)
    
    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password"""
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
        """Encrypt string data"""
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = self.cipher.decrypt(encrypted_bytes)
        return decrypted_data.decode()

# Usage for sensitive fields
encryption = DataEncryption(os.environ.get('ENCRYPTION_PASSWORD'))

class EncryptedObservation:
    """Observation with encrypted sensitive fields"""
    
    def __init__(self, data: dict):
        self.id = data['id']
        self.species_id = data['species_id']
        self.location = data['location']  # Encrypted
        self.notes = data['notes']  # Encrypted
        self.created_at = data['created_at']
    
    @classmethod
    def create(cls, species_id: str, location: dict, notes: str):
        """Create observation with encryption"""
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
        """Get decrypted location data"""
        return json.loads(encryption.decrypt(self.location))
    
    def get_decrypted_notes(self) -> str:
        """Get decrypted notes"""
        return encryption.decrypt(self.notes) if self.notes else ""
```

#### Data in Transit

Ensure all communications use HTTPS/TLS:

```nginx
# Nginx SSL configuration
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL certificates
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # SSL security settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # Other security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';";
}
```

### Data Privacy

#### GDPR Compliance

Implement data privacy controls:

```python
# backend/services/privacy.py
from typing import List, Dict, Any
from datetime import datetime, timedelta

class PrivacyManager:
    """Manage data privacy and GDPR compliance"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user data for GDPR compliance"""
        user_data = {
            "user_id": user_id,
            "export_date": datetime.utcnow().isoformat(),
            "observations": self._get_user_observations(user_id),
            "uploads": self._get_user_uploads(user_id),
            "sessions": self._get_user_sessions(user_id)
        }
        
        return user_data
    
    def delete_user_data(self, user_id: str) -> bool:
        """Delete all user data (right to be forgotten)"""
        try:
            # Delete observations
            self.db.delete_user_observations(user_id)
            
            # Delete uploaded files
            self._delete_user_files(user_id)
            
            # Delete sessions
            self.db.delete_user_sessions(user_id)
            
            # Anonymize remaining references
            self._anonymize_user_references(user_id)
            
            return True
        except Exception as e:
            logging.error(f"Failed to delete user data: {e}")
            return False
    
    def anonymize_old_data(self, days_old: int = 365):
        """Anonymize data older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Anonymize old observations
        old_observations = self.db.get_observations_before(cutoff_date)
        for obs in old_observations:
            self._anonymize_observation(obs)
    
    def _get_user_observations(self, user_id: str) -> List[Dict]:
        """Get all observations for a user"""
        return self.db.get_user_observations(user_id)
    
    def _get_user_uploads(self, user_id: str) -> List[Dict]:
        """Get all file uploads for a user"""
        return self.db.get_user_uploads(user_id)
    
    def _get_user_sessions(self, user_id: str) -> List[Dict]:
        """Get session history for a user"""
        return self.db.get_user_sessions(user_id)
    
    def _delete_user_files(self, user_id: str):
        """Delete all files uploaded by user"""
        user_files = self.db.get_user_files(user_id)
        for file_info in user_files:
            try:
                os.remove(file_info['file_path'])
            except FileNotFoundError:
                pass  # File already deleted
    
    def _anonymize_observation(self, observation: Dict):
        """Anonymize an observation record"""
        # Remove or hash identifying information
        observation['user_id'] = 'anonymous'
        observation['ip_address'] = None
        observation['metadata'] = {}
        
        self.db.update_observation(observation)
    
    def _anonymize_user_references(self, user_id: str):
        """Anonymize references to user in other tables"""
        # Update any remaining references to use anonymous ID
        self.db.update_user_references(user_id, 'anonymous')
```

## Infrastructure Security

### Server Hardening

#### Operating System Security

```bash
#!/bin/bash
# server-hardening.sh

# Update system packages
apt update && apt upgrade -y

# Configure firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Disable unnecessary services
systemctl disable bluetooth
systemctl disable cups
systemctl disable avahi-daemon

# Configure SSH security
sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
systemctl restart sshd

# Install fail2ban
apt install fail2ban -y
systemctl enable fail2ban
systemctl start fail2ban

# Configure automatic security updates
apt install unattended-upgrades -y
dpkg-reconfigure -plow unattended-upgrades

# Set up log monitoring
apt install logwatch -y
echo "logwatch --output mail --mailto admin@example.com --detail high" > /etc/cron.daily/00logwatch
chmod +x /etc/cron.daily/00logwatch
```

#### Docker Security

```dockerfile
# Secure Dockerfile practices
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install security updates
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set proper permissions
RUN chown -R appuser:appuser /app
USER appuser

# Use non-root port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Network Security

#### Firewall Configuration

```bash
# iptables rules for additional security
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -j DROP

# Rate limiting
iptables -A INPUT -p tcp --dport 80 -m limit --limit 25/minute --limit-burst 100 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -m limit --limit 25/minute --limit-burst 100 -j ACCEPT

# Save rules
iptables-save > /etc/iptables/rules.v4
```

#### VPN Access

For administrative access, consider VPN setup:

```bash
# Install WireGuard VPN
apt install wireguard -y

# Generate server keys
wg genkey | tee /etc/wireguard/private.key
cat /etc/wireguard/private.key | wg pubkey | tee /etc/wireguard/public.key

# Configure WireGuard
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

# Enable and start WireGuard
systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0
```

## Security Monitoring

### Intrusion Detection

#### OSSEC Configuration

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
    <include>telnetd_rules.xml</include>
    <include>syslog_rules.xml</include>
    <include>arpwatch_rules.xml</include>
    <include>symantec-av_rules.xml</include>
    <include>symantec-ws_rules.xml</include>
    <include>pix_rules.xml</include>
    <include>named_rules.xml</include>
    <include>smbd_rules.xml</include>
    <include>vsftpd_rules.xml</include>
    <include>pure-ftpd_rules.xml</include>
    <include>proftpd_rules.xml</include>
    <include>ms_ftpd_rules.xml</include>
    <include>ftpd_rules.xml</include>
    <include>hordeimp_rules.xml</include>
    <include>roundcube_rules.xml</include>
    <include>wordpress_rules.xml</include>
    <include>cimserver_rules.xml</include>
    <include>vpopmail_rules.xml</include>
    <include>vmpop3d_rules.xml</include>
    <include>courier_rules.xml</include>
    <include>web_rules.xml</include>
    <include>web_appsec_rules.xml</include>
    <include>apache_rules.xml</include>
    <include>nginx_rules.xml</include>
    <include>php_rules.xml</include>
    <include>mysql_rules.xml</include>
    <include>postgresql_rules.xml</include>
    <include>ids_rules.xml</include>
    <include>squid_rules.xml</include>
    <include>firewall_rules.xml</include>
    <include>cisco-ios_rules.xml</include>
    <include>netscreenfw_rules.xml</include>
    <include>sonicwall_rules.xml</include>
    <include>postfix_rules.xml</include>
    <include>sendmail_rules.xml</include>
    <include>imapd_rules.xml</include>
    <include>mailscanner_rules.xml</include>
    <include>dovecot_rules.xml</include>
    <include>ms-exchange_rules.xml</include>
    <include>racoon_rules.xml</include>
    <include>vpn_concentrator_rules.xml</include>
    <include>spamd_rules.xml</include>
    <include>msauth_rules.xml</include>
    <include>mcafee_av_rules.xml</include>
    <include>trend-osce_rules.xml</include>
    <include>ms-se_rules.xml</include>
    <include>zeus_rules.xml</include>
    <include>solaris_bsm_rules.xml</include>
    <include>vmware_rules.xml</include>
    <include>ms_dhcp_rules.xml</include>
    <include>asterisk_rules.xml</include>
    <include>ossec_rules.xml</include>
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

### Security Alerting

#### Custom Security Alerts

```python
# backend/services/security_alerts.py
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

class SecurityAlertManager:
    """Manage security alerts and notifications"""
    
    def __init__(self):
        self.failed_attempts = defaultdict(list)
        self.suspicious_activities = []
        
    def log_failed_login(self, ip_address: str, user_agent: str):
        """Log failed login attempt"""
        self.failed_attempts[ip_address].append({
            'timestamp': datetime.utcnow(),
            'user_agent': user_agent
        })
        
        # Check for brute force attack
        recent_attempts = [
            attempt for attempt in self.failed_attempts[ip_address]
            if attempt['timestamp'] > datetime.utcnow() - timedelta(minutes=15)
        ]
        
        if len(recent_attempts) >= 5:
            self._trigger_brute_force_alert(ip_address, recent_attempts)
    
    def log_suspicious_activity(self, activity_type: str, details: Dict[str, Any]):
        """Log suspicious activity"""
        alert = {
            'type': activity_type,
            'timestamp': datetime.utcnow(),
            'details': details
        }
        
        self.suspicious_activities.append(alert)
        
        # Trigger immediate alert for critical activities
        if activity_type in ['sql_injection', 'file_upload_malware', 'privilege_escalation']:
            self._trigger_critical_alert(alert)
    
    def _trigger_brute_force_alert(self, ip_address: str, attempts: list):
        """Trigger brute force attack alert"""
        logging.critical(
            "Brute force attack detected",
            extra={
                'security_alert': True,
                'alert_type': 'brute_force',
                'ip_address': ip_address,
                'attempt_count': len(attempts),
                'time_window': '15 minutes'
            }
        )
        
        # Send notification to security team
        self._send_security_notification(
            "Brute Force Attack Detected",
            f"IP {ip_address} has made {len(attempts)} failed login attempts in 15 minutes"
        )
    
    def _trigger_critical_alert(self, alert: Dict[str, Any]):
        """Trigger critical security alert"""
        logging.critical(
            "Critical security event detected",
            extra={
                'security_alert': True,
                'alert_type': alert['type'],
                'details': alert['details']
            }
        )
        
        # Immediate notification
        self._send_security_notification(
            f"Critical Security Alert: {alert['type']}",
            f"Details: {alert['details']}"
        )
    
    def _send_security_notification(self, subject: str, message: str):
        """Send security notification"""
        # Implement notification logic (email, Slack, etc.)
        pass

# Middleware for security monitoring
class SecurityMonitoringMiddleware(BaseHTTPMiddleware):
    """Monitor requests for security threats"""
    
    def __init__(self, app):
        super().__init__(app)
        self.alert_manager = SecurityAlertManager()
    
    async def dispatch(self, request: Request, call_next):
        # Check for suspicious patterns
        self._check_sql_injection(request)
        self._check_xss_attempts(request)
        self._check_path_traversal(request)
        
        response = await call_next(request)
        
        # Log failed authentication attempts
        if response.status_code == 401:
            self.alert_manager.log_failed_login(
                request.client.host,
                request.headers.get('user-agent', '')
            )
        
        return response
    
    def _check_sql_injection(self, request: Request):
        """Check for SQL injection attempts"""
        sql_patterns = [
            r"union\s+select",
            r"drop\s+table",
            r"insert\s+into",
            r"delete\s+from",
            r"update\s+.*set",
            r"exec\s*\(",
            r"script\s*>",
            r"<\s*script"
        ]
        
        query_string = str(request.url.query).lower()
        
        for pattern in sql_patterns:
            if re.search(pattern, query_string):
                self.alert_manager.log_suspicious_activity(
                    'sql_injection',
                    {
                        'ip_address': request.client.host,
                        'url': str(request.url),
                        'pattern': pattern,
                        'user_agent': request.headers.get('user-agent', '')
                    }
                )
                break
    
    def _check_xss_attempts(self, request: Request):
        """Check for XSS attempts"""
        xss_patterns = [
            r"<script",
            r"javascript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*="
        ]
        
        query_string = str(request.url.query).lower()
        
        for pattern in xss_patterns:
            if re.search(pattern, query_string):
                self.alert_manager.log_suspicious_activity(
                    'xss_attempt',
                    {
                        'ip_address': request.client.host,
                        'url': str(request.url),
                        'pattern': pattern
                    }
                )
                break
    
    def _check_path_traversal(self, request: Request):
        """Check for path traversal attempts"""
        path = str(request.url.path)
        
        if '../' in path or '..\\' in path:
            self.alert_manager.log_suspicious_activity(
                'path_traversal',
                {
                    'ip_address': request.client.host,
                    'path': path
                }
            )
```

## Incident Response

### Security Incident Playbook

#### 1. Detection and Analysis

```python
# backend/services/incident_response.py
from enum import Enum
from typing import List, Dict, Any
from datetime import datetime

class IncidentSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityIncident:
    """Security incident management"""
    
    def __init__(self, incident_type: str, severity: IncidentSeverity, description: str):
        self.id = str(uuid.uuid4())
        self.type = incident_type
        self.severity = severity
        self.description = description
        self.created_at = datetime.utcnow()
        self.status = "open"
        self.actions_taken = []
        self.affected_systems = []
    
    def add_action(self, action: str, performed_by: str):
        """Add action taken during incident response"""
        self.actions_taken.append({
            'timestamp': datetime.utcnow(),
            'action': action,
            'performed_by': performed_by
        })
    
    def add_affected_system(self, system: str):
        """Add affected system to incident"""
        if system not in self.affected_systems:
            self.affected_systems.append(system)
    
    def close_incident(self, resolution: str):
        """Close the incident"""
        self.status = "closed"
        self.resolution = resolution
        self.closed_at = datetime.utcnow()

class IncidentResponseManager:
    """Manage security incident response"""
    
    def __init__(self):
        self.active_incidents = {}
        self.incident_history = []
    
    def create_incident(self, incident_type: str, severity: IncidentSeverity, 
                       description: str) -> SecurityIncident:
        """Create new security incident"""
        incident = SecurityIncident(incident_type, severity, description)
        self.active_incidents[incident.id] = incident
        
        # Trigger immediate response for critical incidents
        if severity == IncidentSeverity.CRITICAL:
            self._trigger_emergency_response(incident)
        
        return incident
    
    def _trigger_emergency_response(self, incident: SecurityIncident):
        """Trigger emergency response procedures"""
        # Immediate actions for critical incidents
        actions = [
            "Notify security team immediately",
            "Isolate affected systems if necessary",
            "Begin evidence collection",
            "Activate incident response team"
        ]
        
        for action in actions:
            incident.add_action(action, "automated_system")
        
        # Send emergency notifications
        self._send_emergency_notification(incident)
    
    def _send_emergency_notification(self, incident: SecurityIncident):
        """Send emergency notification to response team"""
        # Implement emergency notification logic
        pass
```

#### 2. Containment and Eradication

```bash
#!/bin/bash
# incident-containment.sh

# Isolate compromised system
iptables -A INPUT -s COMPROMISED_IP -j DROP
iptables -A OUTPUT -d COMPROMISED_IP -j DROP

# Stop affected services
systemctl stop culicidaelab-backend
systemctl stop culicidaelab-frontend

# Create forensic image
dd if=/dev/sda of=/forensics/system-image-$(date +%Y%m%d-%H%M%S).img bs=4M

# Preserve logs
cp -r /var/log /forensics/logs-$(date +%Y%m%d-%H%M%S)

# Change all passwords
passwd root
# Change application passwords and API keys

# Update and patch system
apt update && apt upgrade -y

# Scan for malware
clamscan -r /app --log=/forensics/malware-scan.log

# Restart services with new configuration
systemctl start culicidaelab-backend
systemctl start culicidaelab-frontend
```

### Recovery and Lessons Learned

#### Post-Incident Analysis

```python
# backend/services/post_incident.py
class PostIncidentAnalysis:
    """Conduct post-incident analysis"""
    
    def __init__(self, incident: SecurityIncident):
        self.incident = incident
        self.timeline = []
        self.root_causes = []
        self.recommendations = []
    
    def analyze_incident(self) -> Dict[str, Any]:
        """Analyze incident and generate report"""
        
        # Build timeline
        self._build_timeline()
        
        # Identify root causes
        self._identify_root_causes()
        
        # Generate recommendations
        self._generate_recommendations()
        
        return {
            'incident_id': self.incident.id,
            'timeline': self.timeline,
            'root_causes': self.root_causes,
            'recommendations': self.recommendations,
            'lessons_learned': self._extract_lessons_learned()
        }
    
    def _build_timeline(self):
        """Build incident timeline"""
        # Analyze logs and actions to build timeline
        pass
    
    def _identify_root_causes(self):
        """Identify root causes of incident"""
        # Analyze incident data to identify causes
        pass
    
    def _generate_recommendations(self):
        """Generate security improvement recommendations"""
        common_recommendations = [
            "Implement additional monitoring",
            "Update security policies",
            "Conduct security training",
            "Review access controls",
            "Update incident response procedures"
        ]
        
        self.recommendations.extend(common_recommendations)
    
    def _extract_lessons_learned(self) -> List[str]:
        """Extract lessons learned from incident"""
        return [
            "Importance of rapid detection",
            "Need for automated response",
            "Value of regular security training",
            "Critical nature of backup systems"
        ]
```

## Security Best Practices Summary

### Development Security

1. **Secure Coding Practices**
   - Input validation and sanitization
   - Output encoding
   - Parameterized queries
   - Error handling without information disclosure

2. **Dependency Management**
   - Regular security updates
   - Vulnerability scanning
   - License compliance
   - Minimal dependencies

3. **Code Review**
   - Security-focused code reviews
   - Automated security testing
   - Static code analysis
   - Penetration testing

### Deployment Security

1. **Infrastructure Hardening**
   - Server hardening
   - Network segmentation
   - Access controls
   - Regular updates

2. **Monitoring and Alerting**
   - Real-time monitoring
   - Security event correlation
   - Incident response procedures
   - Regular security assessments

3. **Data Protection**
   - Encryption at rest and in transit
   - Access logging
   - Data retention policies
   - Privacy compliance

### Operational Security

1. **Access Management**
   - Principle of least privilege
   - Multi-factor authentication
   - Regular access reviews
   - Secure credential storage

2. **Backup and Recovery**
   - Regular backups
   - Backup encryption
   - Recovery testing
   - Disaster recovery planning

3. **Compliance and Auditing**
   - Regular security audits
   - Compliance monitoring
   - Documentation maintenance
   - Staff training