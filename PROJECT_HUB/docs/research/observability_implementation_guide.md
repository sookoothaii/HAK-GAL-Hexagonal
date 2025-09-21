---
title: "Observability Stack Implementation Guide"
created: "2025-09-21T10:15:00.000000Z"
author: "Claude-Sonnet-4"
topics: ["observability", "prometheus", "grafana", "jaeger", "elk_stack"]
tags: ["implementation-guide", "monitoring", "metrics", "tracing", "logging"]
privacy: "internal"
summary_200: "Detaillierte Implementierungsanleitung für den vollständigen Observability-Stack mit Prometheus, Grafana, Jaeger und ELK-Stack für die HAK-GAL Architektur."
---

# Observability Stack Implementation Guide

**Version:** 1.0  
**Datum:** 2025-09-21  
**Autor:** Claude-Sonnet-4  
**Status:** Implementation Guide  
**Priorität:** KRITISCH (3 Monate)

## 🎯 Implementierungsübersicht

### Aktuelle Situation
- **Observability Score:** 2/10 (Kritisch unterentwickelt)
- **Vorhanden:** Basic health checks, stdout logging
- **Fehlt:** Prometheus, Grafana, Jaeger, ELK-Stack

### Ziel-Architektur
```
┌─────────────────────────────────────────────────────────────────┐
│                    OBSERVABILITY STACK                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │ Prometheus  │  │   Grafana   │  │   Jaeger    │  │ ELK     │ │
│  │ (Metrics)   │  │(Dashboards) │  │ (Tracing)   │  │(Logs)   │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │    Caddy    │  │    Flask    │  │    React    │  │ SQLite  │ │
│  │ (Port 8088) │  │ (Port 5002) │  │ (Port 5173) │  │ (DB)    │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 Phase 1: Prometheus Metrics Collection

### 1.1 Prometheus Server Setup

#### Docker Compose Configuration
```yaml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'

volumes:
  prometheus_data:
```

#### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'caddy'
    static_configs:
      - targets: ['caddy:8088']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'flask-backend'
    static_configs:
      - targets: ['flask:5002']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'react-frontend'
    static_configs:
      - targets: ['react:5173']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'sqlite-db'
    static_configs:
      - targets: ['db-exporter:9117']
    scrape_interval: 30s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### 1.2 Flask Backend Instrumentation

#### Requirements
```python
# requirements.txt
prometheus-client==0.19.0
flask-prometheus-metrics==1.2.0
```

#### Flask App Instrumentation
```python
# app.py
from flask import Flask
from prometheus_client import Counter, Histogram, generate_latest
import time

app = Flask(__name__)

# Prometheus Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
VALIDATION_COUNT = Counter('fact_validations_total', 'Total fact validations', ['validator', 'result'])

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    request_duration = time.time() - request.start_time
    REQUEST_DURATION.observe(request_duration)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.endpoint,
        status=response.status_code
    ).inc()
    return response

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': 'text/plain'}

# Hallucination Prevention Metrics
def record_validation(validator, is_valid):
    result = 'valid' if is_valid else 'invalid'
    VALIDATION_COUNT.labels(validator=validator, result=result).inc()
```

### 1.3 Caddy Proxy Metrics

#### Caddy Configuration Update
```caddyfile
{
    admin off
    metrics
}

:8088 {
    metrics /metrics
    
    # ... existing configuration ...
}
```

### 1.4 React Frontend Metrics

#### Web Vitals Integration
```typescript
// src/utils/metrics.ts
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

export function initMetrics() {
  getCLS(sendToPrometheus);
  getFID(sendToPrometheus);
  getFCP(sendToPrometheus);
  getLCP(sendToPrometheus);
  getTTFB(sendToPrometheus);
}

function sendToPrometheus(metric: any) {
  // Send to Prometheus via backend
  fetch('/api/metrics', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: metric.name,
      value: metric.value,
      delta: metric.delta,
      id: metric.id
    })
  });
}
```

## 📈 Phase 2: Grafana Dashboard Visualization

### 2.1 Grafana Setup

#### Docker Compose Addition
```yaml
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
      - ./grafana/dashboards:/var/lib/grafana/dashboards

volumes:
  grafana_data:
```

### 2.2 Dashboard Configuration

#### System Health Dashboard
```json
{
  "dashboard": {
    "title": "HAK-GAL System Health",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Fact Validation Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(fact_validations_total[5m])",
            "legendFormat": "{{validator}} {{result}}"
          }
        ]
      }
    ]
  }
}
```

## 🔍 Phase 3: Jaeger Distributed Tracing

### 3.1 Jaeger Setup

#### Docker Compose Addition
```yaml
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"
      - "14268:14268"
    environment:
      - COLLECTOR_OTLP_ENABLED=true
```

### 3.2 Flask Tracing Integration

#### Requirements
```python
# requirements.txt
opentelemetry-api==1.20.0
opentelemetry-sdk==1.20.0
opentelemetry-instrumentation-flask==0.41b0
opentelemetry-exporter-jaeger==1.20.0
```

#### Flask Tracing Setup
```python
# tracing.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor

def init_tracing(app):
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",
        agent_port=14268,
    )
    
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    FlaskInstrumentor().instrument_app(app)
```

## 📝 Phase 4: ELK Stack Logging

### 4.1 ELK Stack Setup

#### Docker Compose Addition
```yaml
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
    ports:
      - "5044:5044"

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200

volumes:
  elasticsearch_data:
```

### 4.2 Structured Logging Implementation

#### Flask Logging
```python
# logging_config.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
            
        return json.dumps(log_entry)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)
logger.handlers[0].setFormatter(JSONFormatter())
```

## 🚨 Phase 5: Alerting System

### 5.1 AlertManager Setup

#### Docker Compose Addition
```yaml
  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
```

#### Alert Rules
```yaml
# alert_rules.yml
groups:
- name: hak-gal-alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      
  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
```

## 🎯 Erfolgsmetriken

### Quantitative Ziele
- **Metrics Collection Rate:** 99%
- **Dashboard Response Time:** <100ms
- **Trace Completion Rate:** 95%
- **Log Ingestion Rate:** 1000 events/second

### Qualitative Ziele
- Vollständige System-Transparenz
- Proaktive Problem-Erkennung
- Root-Cause-Analysis Capability
- Performance-Optimierung Insights

## 🔗 Knowledge Base Integration

### Forschungs-Facts
- `ObservabilityResearchPriority` - Hauptforschungsrichtung
- `ArchitectureResearchDirection2024` - Gesamtkontext

### Nächste Schritte
1. **Prometheus Setup** (Woche 1-2)
2. **Grafana Dashboards** (Woche 3-4)
3. **Jaeger Tracing** (Woche 5-6)
4. **ELK Stack** (Woche 7-8)
5. **Alerting System** (Woche 9-12)

---

**Dokumentation erstellt:** 2025-09-21  
**Implementierungszeitraum:** 3 Monate  
**Status:** Kritische Priorität  
**Ziel:** Observability Score 2/10 → 8/10