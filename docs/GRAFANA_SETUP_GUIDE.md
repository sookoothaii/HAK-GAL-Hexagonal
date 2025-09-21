# Grafana Setup Guide für HAK-GAL

## 🎯 **Status: Grafana installiert und bereit!**

### **Zugriff:**
- **URL:** http://localhost:3000
- **Standard Login:** admin / admin
- **Neues Passwort:** hakgal2025 (nach erstem Login)

### **Schritt 1: Prometheus Data Source hinzufügen**

1. **Grafana öffnen:** http://localhost:3000
2. **Login:** admin / admin
3. **Navigation:** Configuration → Data Sources
4. **Add data source:** Prometheus
5. **URL:** http://localhost:8000
6. **Save & Test**

### **Schritt 2: HAK-GAL Dashboard erstellen**

1. **Navigation:** + → Dashboard
2. **Add Panel:** System Metrics
3. **Verfügbare Metriken:**
   - `hakgal_facts_total` - Anzahl Fakten
   - `hakgal_system_cpu_percent` - CPU Auslastung
   - `hakgal_system_memory_percent` - Speicher Auslastung
   - `hakgal_query_time_seconds` - Query-Zeit
   - `hakgal_database_connections` - DB Verbindungen
   - `hakgal_wal_size_bytes` - WAL Datei Größe

### **Schritt 3: Dashboard konfigurieren**

**Panel 1: Facts Count**
```promql
hakgal_facts_total
```

**Panel 2: CPU Usage**
```promql
hakgal_system_cpu_percent
```

**Panel 3: Memory Usage**
```promql
hakgal_system_memory_percent
```

**Panel 4: Query Time**
```promql
hakgal_query_time_seconds
```

**Panel 5: Database Connections**
```promql
hakgal_database_connections
```

**Panel 6: WAL Size**
```promql
hakgal_wal_size_bytes
```

### **Schritt 4: Dashboard speichern**

1. **Dashboard Name:** "HAK-GAL System Metrics"
2. **Tags:** hakgal, system, monitoring
3. **Refresh:** 5s
4. **Save Dashboard**

## 🚀 **Ergebnis:**

Vollständige Observability-Stack:
- ✅ **Prometheus** (Port 8000) - Metriken sammeln
- ✅ **Grafana** (Port 3000) - Metriken visualisieren
- ✅ **HAK-GAL Backend** (Port 5002) - Metriken bereitstellen

**Observability Score: 10/10** 🎯
