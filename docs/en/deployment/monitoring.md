# Monitoring and Logging

This guide covers comprehensive monitoring and logging strategies for CulicidaeLab Server, including application metrics, performance monitoring, log management, and alerting systems.

## Overview

Effective monitoring and logging are crucial for maintaining a healthy production environment. This document covers:

- Application health monitoring
- Performance metrics collection
- Log aggregation and analysis
- Alerting and notification systems
- Troubleshooting and debugging

## Application Health Monitoring

### Health Check Endpoints

CulicidaeLab Server provides several health check endpoints for monitoring:

#### Basic Health Check
```http
GET /health
```

Response:
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Detailed API Health Check
```http
GET /api/health
```

Response:
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T12:00:00Z",
  "database": {
    "status": "connected",
    "response_time_ms": 15
  },
  "models": {
    "segmenter": {
      "status": "loaded",
      "load_time_ms": 2500
    }
  },
  "memory": {
    "used_mb": 1024,
    "available_mb": 2048
  }
}
```

### Custom Health Checks

Implement custom health checks for critical components:

```python
# backend/services/health.py
from typing import Dict, Any
import time
import psutil
from backend.services.database import get_db
from backend.config import get_predictor_model_path

async def check_database_health() -> Dict[str, Any]:
    """Check database connectivity and performance"""
    start_time = time.time()
    try:
        db = get_db()
        # Perform a simple query
        result = db.query("SELECT 1").limit(1).to_list()
        response_time = (time.time() - start_time) * 1000
        
        return {
            "status": "connected",
            "response_time_ms": round(response_time, 2)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

async def check_model_health() -> Dict[str, Any]:
    """Check model availability and loading status"""
    try:
        model_path = get_predictor_model_path()
        if not os.path.exists(model_path):
            return {
                "status": "error",
                "error": "Model file not found"
            }
        
        # Check if model can be loaded (simplified check)
        return {
            "status": "loaded",
            "path": model_path
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

async def check_system_resources() -> Dict[str, Any]:
    """Check system resource usage"""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "memory": {
            "used_mb": round(memory.used / 1024 / 1024, 2),
            "available_mb": round(memory.available / 1024 / 1024, 2),
            "percent": memory.percent
        },
        "disk": {
            "used_gb": round(disk.used / 1024 / 1024 / 1024, 2),
            "free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
            "percent": round((disk.used / disk.total) * 100, 2)
        }
    }
```

## Performance Metrics

### Application Metrics

#### Request Metrics
- Request count per endpoint
- Response time percentiles (p50, p95, p99)
- Error rates by status code
- Concurrent request count

#### Model Performance Metrics
- Prediction latency
- Model loading time
- Prediction accuracy (if ground truth available)
- Memory usage during inference

#### Database Metrics
- Query execution time
- Connection pool usage
- Database size and growth
- Index performance

### Metrics Collection with Prometheus

Install and configure Prometheus metrics:

```bash
# Add to pyproject.toml
pip install prometheus-client
```

```python
# backend/services/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
from functools import wraps

# Define metrics
REQUEST_COUNT = Counter(
    'culicidaelab_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'culicidaelab_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

PREDICTION_DURATION = Histogram(
    'culicidaelab_prediction_duration_seconds',
    'Model prediction duration in seconds',
    ['model_type']
)

ACTIVE_CONNECTIONS = Gauge(
    'culicidaelab_active_connections',
    'Number of active database connections'
)

MODEL_MEMORY_USAGE = Gauge(
    'culicidaelab_model_memory_mb',
    'Memory usage by loaded models in MB',
    ['model_name']
)

def track_requests(func):
    """Decorator to track request metrics"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        status = "200"
        
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            status = "500"
            raise
        finally:
            duration = time.time() - start_time
            REQUEST_DURATION.labels(
                method="POST",  # Adjust based on actual method
                endpoint=func.__name__
            ).observe(duration)
            REQUEST_COUNT.labels(
                method="POST",
                endpoint=func.__name__,
                status=status
            ).inc()
    
    return wrapper

def track_prediction_time(model_type: str):
    """Decorator to track prediction timing"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                PREDICTION_DURATION.labels(model_type=model_type).observe(duration)
        return wrapper
    return decorator

# Metrics endpoint
from fastapi import Response

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        generate_latest(),
        media_type="text/plain"
    )
```

### Metrics Dashboard with Grafana

Create Grafana dashboard configuration:

```json
{
  "dashboard": {
    "title": "CulicidaeLab Server Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(culicidaelab_requests_total[5m])",
            "legendFormat": "{{endpoint}} - {{status}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(culicidaelab_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(culicidaelab_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          }
        ]
      },
      {
        "title": "Prediction Latency",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(culicidaelab_prediction_duration_seconds_bucket[5m]))",
            "legendFormat": "{{model_type}} - 95th percentile"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "culicidaelab_model_memory_mb",
            "legendFormat": "{{model_name}}"
          }
        ]
      }
    ]
  }
}
```

## Logging Configuration

### Structured Logging

Configure structured logging for better analysis:

```python
# backend/services/logging.py
import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'duration_ms'):
            log_entry['duration_ms'] = record.duration_ms
        if hasattr(record, 'status_code'):
            log_entry['status_code'] = record.status_code
            
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry)

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Configure application logging"""
    
    # Create logger
    logger = logging.getLogger("culicidaelab")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = JSONFormatter()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Request logging middleware
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests and responses"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Log request
        logger = logging.getLogger("culicidaelab.requests")
        start_time = time.time()
        
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "user_agent": request.headers.get("user-agent"),
                "client_ip": request.client.host
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            logger.error(
                "Request failed with exception",
                extra={
                    "request_id": request_id,
                    "exception": str(e)
                },
                exc_info=True
            )
            raise
        finally:
            # Log response
            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "status_code": status_code,
                    "duration_ms": round(duration_ms, 2)
                }
            )
        
        return response
```

### Log Aggregation

#### ELK Stack (Elasticsearch, Logstash, Kibana)

Docker Compose configuration for ELK stack:

```yaml
# docker-compose.elk.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    ports:
      - "5044:5044"
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  elasticsearch_data:
```

Logstash configuration (`logstash.conf`):

```ruby
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "culicidaelab" {
    json {
      source => "message"
    }
    
    date {
      match => [ "timestamp", "ISO8601" ]
    }
    
    if [level] == "ERROR" or [level] == "CRITICAL" {
      mutate {
        add_tag => [ "error" ]
      }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "culicidaelab-logs-%{+YYYY.MM.dd}"
  }
}
```

#### Filebeat Configuration

Configure Filebeat to ship logs to Logstash:

```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/culicidaelab/*.log
  fields:
    service: culicidaelab
  fields_under_root: true
  json.keys_under_root: true
  json.add_error_key: true

output.logstash:
  hosts: ["logstash:5044"]

processors:
  - add_host_metadata:
      when.not.contains.tags: forwarded
```

### Log Analysis and Alerting

#### Kibana Dashboards

Create Kibana visualizations for:

1. **Request Volume**: Requests per minute/hour
2. **Error Rate**: Error percentage over time
3. **Response Time**: Response time percentiles
4. **Geographic Distribution**: Request origins on map
5. **User Activity**: Active users and sessions

#### Log-based Alerts

Configure alerts for critical events:

```json
{
  "alert": {
    "name": "High Error Rate",
    "condition": {
      "query": {
        "bool": {
          "must": [
            {"term": {"level": "ERROR"}},
            {"range": {"@timestamp": {"gte": "now-5m"}}}
          ]
        }
      },
      "threshold": 10
    },
    "actions": [
      {
        "type": "email",
        "to": ["admin@culicidaelab.com"],
        "subject": "CulicidaeLab: High Error Rate Alert"
      },
      {
        "type": "slack",
        "webhook": "https://hooks.slack.com/...",
        "message": "High error rate detected in CulicidaeLab"
      }
    ]
  }
}
```

## System Monitoring

### Infrastructure Monitoring

#### Server Metrics

Monitor key system metrics:

- CPU usage and load average
- Memory usage and swap
- Disk usage and I/O
- Network traffic and connections
- Process count and status

#### Docker Monitoring

For containerized deployments:

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

  node-exporter:
    image: prom/node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro

  cadvisor:
    image: gcr.io/cadvisor/cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro

volumes:
  prometheus_data:
  grafana_data:
```

### Database Monitoring

Monitor LanceDB performance:

```python
# backend/services/db_monitoring.py
import time
import psutil
from typing import Dict, Any

class DatabaseMonitor:
    """Monitor database performance and health"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def get_database_metrics(self) -> Dict[str, Any]:
        """Collect database performance metrics"""
        
        # Database size
        db_size = self._get_directory_size(self.db_path)
        
        # Query performance (example)
        query_times = self._measure_query_performance()
        
        # Connection count (if applicable)
        connection_count = self._get_connection_count()
        
        return {
            "size_mb": round(db_size / 1024 / 1024, 2),
            "query_times": query_times,
            "connections": connection_count,
            "timestamp": time.time()
        }
    
    def _get_directory_size(self, path: str) -> int:
        """Calculate directory size in bytes"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        return total_size
    
    def _measure_query_performance(self) -> Dict[str, float]:
        """Measure query execution times"""
        # Implement query timing logic
        return {
            "avg_query_time_ms": 15.5,
            "max_query_time_ms": 150.0,
            "queries_per_second": 25.0
        }
    
    def _get_connection_count(self) -> int:
        """Get active connection count"""
        # Implement connection counting logic
        return 5
```

## Alerting and Notifications

### Alert Rules

Define alert rules for critical conditions:

```yaml
# prometheus-alerts.yml
groups:
  - name: culicidaelab-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(culicidaelab_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(culicidaelab_request_duration_seconds_bucket[5m])) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }} seconds"

      - alert: DatabaseConnectionFailure
        expr: up{job="culicidaelab-backend"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database connection failure"
          description: "Cannot connect to database"

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value | humanizePercentage }}"

      - alert: DiskSpaceLow
        expr: (node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes > 0.85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low disk space"
          description: "Disk usage is {{ $value | humanizePercentage }}"
```

### Notification Channels

#### Email Notifications

```python
# backend/services/notifications.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailNotifier:
    """Send email notifications for alerts"""
    
    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    def send_alert(self, to_email: str, subject: str, message: str):
        """Send alert email"""
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'plain'))
        
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
```

#### Slack Notifications

```python
import requests
import json

class SlackNotifier:
    """Send Slack notifications for alerts"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_alert(self, message: str, severity: str = "warning"):
        """Send alert to Slack"""
        color_map = {
            "critical": "#FF0000",
            "warning": "#FFA500",
            "info": "#00FF00"
        }
        
        payload = {
            "attachments": [
                {
                    "color": color_map.get(severity, "#808080"),
                    "title": f"CulicidaeLab Alert - {severity.upper()}",
                    "text": message,
                    "ts": int(time.time())
                }
            ]
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
        except Exception as e:
            logging.error(f"Failed to send Slack notification: {e}")
```

## Troubleshooting and Debugging

### Log Analysis Queries

Common log analysis queries for troubleshooting:

#### Find Error Patterns
```json
{
  "query": {
    "bool": {
      "must": [
        {"term": {"level": "ERROR"}},
        {"range": {"@timestamp": {"gte": "now-1h"}}}
      ]
    }
  },
  "aggs": {
    "error_messages": {
      "terms": {
        "field": "message.keyword",
        "size": 10
      }
    }
  }
}
```

#### Performance Analysis
```json
{
  "query": {
    "bool": {
      "must": [
        {"exists": {"field": "duration_ms"}},
        {"range": {"duration_ms": {"gte": 1000}}}
      ]
    }
  },
  "sort": [
    {"duration_ms": {"order": "desc"}}
  ]
}
```

#### User Activity Tracking
```json
{
  "query": {
    "bool": {
      "must": [
        {"exists": {"field": "user_id"}},
        {"range": {"@timestamp": {"gte": "now-24h"}}}
      ]
    }
  },
  "aggs": {
    "unique_users": {
      "cardinality": {
        "field": "user_id"
      }
    }
  }
}
```

### Performance Debugging

#### Memory Profiling

```python
# backend/services/profiling.py
import tracemalloc
import psutil
import gc
from functools import wraps

def profile_memory(func):
    """Decorator to profile memory usage"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Start tracing
        tracemalloc.start()
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            # Get memory statistics
            current, peak = tracemalloc.get_traced_memory()
            final_memory = process.memory_info().rss
            tracemalloc.stop()
            
            # Log memory usage
            logging.info(
                "Memory profile",
                extra={
                    "function": func.__name__,
                    "current_mb": round(current / 1024 / 1024, 2),
                    "peak_mb": round(peak / 1024 / 1024, 2),
                    "process_delta_mb": round((final_memory - initial_memory) / 1024 / 1024, 2)
                }
            )
    
    return wrapper
```

#### Database Query Profiling

```python
def profile_query(func):
    """Decorator to profile database queries"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            
            # Log slow queries
            if duration > 1.0:  # Log queries taking more than 1 second
                logging.warning(
                    "Slow query detected",
                    extra={
                        "function": func.__name__,
                        "duration_seconds": round(duration, 3),
                        "args": str(args)[:100]  # Truncate for logging
                    }
                )
    
    return wrapper
```

### Monitoring Best Practices

1. **Set Appropriate Thresholds**: Configure alert thresholds based on baseline performance
2. **Avoid Alert Fatigue**: Don't over-alert; focus on actionable alerts
3. **Monitor Business Metrics**: Track user engagement and feature usage
4. **Regular Review**: Periodically review and update monitoring configuration
5. **Documentation**: Document alert procedures and escalation paths
6. **Testing**: Test monitoring and alerting systems regularly
7. **Retention Policies**: Set appropriate log and metric retention periods
8. **Security**: Secure monitoring infrastructure and access controls