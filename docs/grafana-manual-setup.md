# Grafana Manual Setup - Einfachste Lösung

## 🔐 **Problem:** 401 Unauthorized
Das passiert, weil Grafana API-Authentifizierung benötigt und das Standard-Passwort nicht funktioniert.

## ✅ **Lösung: Manuelle Konfiguration über Web-UI**

### **Schritt 1: Grafana öffnen**
- **URL:** http://localhost:3000
- **Login:** admin / [Ihr gesetztes Passwort]

### **Schritt 2: Prometheus Data Source hinzufügen**
1. **Navigation:** Configuration → Data Sources
2. **"Add data source" klicken**
3. **"Prometheus" auswählen**
4. **Konfiguration:**
   - **Name:** `HAK-GAL Prometheus`
   - **URL:** `http://localhost:8000`
   - **Access:** `Server (default)`
   - **HTTP Method:** `GET`
5. **"Save & Test" klicken**
6. **Erwartete Meldung:** "Data source is working"

### **Schritt 3: Dashboard erstellen**
1. **Navigation:** + → Dashboard
2. **"Add panel" klicken**
3. **Panel konfigurieren:**
   - **Query:** `hakgal_facts_total`
   - **Visualization:** Stat
   - **Panel Title:** "Facts Count"
4. **"Apply" klicken**

### **Schritt 4: Weitere Panels hinzufügen**
Wiederholen Sie Schritt 3 für:
- **CPU Usage:** `hakgal_system_cpu_percent`
- **Memory Usage:** `hakgal_system_memory_percent`
- **Query Time:** `hakgal_query_time_seconds`
- **DB Connections:** `hakgal_database_connections`
- **WAL Size:** `hakgal_wal_size_bytes`

### **Schritt 5: Dashboard speichern**
1. **Dashboard Name:** "HAK-GAL System Metrics"
2. **Tags:** hakgal, system, monitoring
3. **Refresh:** 5s
4. **"Save dashboard" klicken**

## 🎯 **Ergebnis:**
Vollständiges HAK-GAL Monitoring Dashboard mit allen System-Metriken!

## 🚀 **Warum manuell besser ist:**
- ✅ Keine Authentifizierungsprobleme
- ✅ Sofortige visuelle Bestätigung
- ✅ Einfache Anpassungen möglich
- ✅ Keine Script-Abhängigkeiten
