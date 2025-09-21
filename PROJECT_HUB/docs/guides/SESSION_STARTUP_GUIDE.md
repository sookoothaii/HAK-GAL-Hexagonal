---
title: "HAK_GAL Session Startup Guide - Complete Reference"
created: "2025-01-17T02:00:00Z"
author: "claude-sonnet-4"
topics: ["guides", "startup", "session_management"]
tags: ["startup", "session", "guide", "reference", "quick-start"]
privacy: "internal"
summary_200: |-
  Complete guide for starting new HAK_GAL sessions. Includes system initialization, service startup, 
  verification steps, and troubleshooting. Covers all ports, services, and integration points.
---

# 🚀 HAK_GAL Session Startup Guide - Complete Reference

## 📋 **QUICK START CHECKLIST**

### **1. Environment Setup**
```bash
# Activate virtual environment
.\.venv_hexa\Scripts\Activate.ps1

# Verify Python environment
python --version  # Should show Python 3.x
```

### **2. Service Startup**
```bash
# Start backend services
python src_hexagonal/hexagonal_api_enhanced_clean.py

# Start frontend (separate terminal)
cd frontend && npm run dev

# Start monitoring (optional)
python start_prometheus.py
```

### **3. Verification**
```bash
# Check backend health
curl http://localhost:5002/health

# Check frontend
curl http://localhost:5173

# Check monitoring
curl http://localhost:5000  # Dashboard
curl http://localhost:8000  # Prometheus
```

## 🔧 **DETAILED STARTUP PROCEDURE**

### **Step 1: System Initialization**
1. **Navigate to project directory:**
   ```bash
   cd "D:\MCP Mods\HAK_GAL_HEXAGONAL"
   ```

2. **Activate virtual environment:**
   ```bash
   .\.venv_hexa\Scripts\Activate.ps1
   ```

3. **Verify environment:**
   ```bash
   python --version
   pip list | findstr -i "flask\|socketio\|sqlite"
   ```

### **Step 2: Backend Services**
1. **Start main API server:**
   ```bash
   python src_hexagonal/hexagonal_api_enhanced_clean.py
   ```
   - **Port:** 5002
   - **Health Check:** http://localhost:5002/health
   - **API Docs:** http://localhost:5002/api/status

2. **Verify backend:**
   ```bash
   curl http://localhost:5002/health
   # Expected: {"status": "healthy", "timestamp": "..."}
   ```

### **Step 3: Frontend Services**
1. **Start React development server:**
   ```bash
   cd frontend
   npm run dev
   ```
   - **Port:** 5173
   - **URL:** http://localhost:5173

2. **Start Caddy proxy (optional):**
   ```bash
   caddy run --config Caddyfile
   ```
   - **Port:** 8088
   - **URL:** http://localhost:8088

### **Step 4: Monitoring Services**
1. **Start Prometheus:**
   ```bash
   python start_prometheus.py
   ```
   - **Port:** 8000
   - **URL:** http://localhost:8000

2. **Start Dashboard:**
   ```bash
   python start_dashboard.py
   ```
   - **Port:** 5000
   - **URL:** http://localhost:5000

## 🌐 **PORT ARCHITECTURE**

| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| **Backend API** | 5002 | Main Flask server | ✅ Active |
| **Frontend** | 5173 | React development | ✅ Active |
| **Caddy Proxy** | 8088 | Frontend/Backend proxy | ✅ Active |
| **Dashboard** | 5000 | Monitoring dashboard | ✅ Active |
| **Prometheus** | 8000 | Metrics collection | ✅ Active |
| **WebSocket** | 5002 | Real-time communication | ✅ Active |

## 🔍 **VERIFICATION STEPS**

### **Backend Health Check:**
```bash
# Basic health
curl http://localhost:5002/health

# API status
curl http://localhost:5002/api/status

# Facts count
curl http://localhost:5002/api/facts/count

# Governance status
curl http://localhost:5002/api/governance/status
```

### **Frontend Verification:**
```bash
# React app
curl http://localhost:5173

# Caddy proxy
curl http://localhost:8088
```

### **Monitoring Verification:**
```bash
# Dashboard
curl http://localhost:5000

# Prometheus
curl http://localhost:8000
```

## 🧪 **LLM GOVERNOR TESTING**

### **Test Mock Provider:**
```bash
python test_ollama_integration.py --mock
```

### **Test Ollama Integration:**
```bash
# Check Ollama status
ollama list

# Test integration
python test_ollama_integration.py
```

### **Test Groq Cloud:**
```bash
# Set API key
$env:GROQ_API_KEY="<YOUR_GROQ_API_KEY_HERE>"

# Test integration
python test_groq_integration.py
```

### **Test Hybrid Governor:**
```bash
python test_hybrid_groq.py
```

## 🔧 **TROUBLESHOOTING**

### **Common Issues:**

#### **1. Virtual Environment Not Found:**
```bash
# Error: venv_hexa not found
# Solution: Use correct path
.\.venv_hexa\Scripts\Activate.ps1  # Note the dot prefix
```

#### **2. Port Already in Use:**
```bash
# Check port usage
netstat -ano | findstr :5002

# Kill process if needed
taskkill /PID <PID> /F
```

#### **3. Ollama Not Running:**
```bash
# Start Ollama service
ollama serve

# Check status
ollama list
```

#### **4. Groq API Key Missing:**
```bash
# Set environment variable
$env:GROQ_API_KEY="your_api_key_here"

# Verify
echo $env:GROQ_API_KEY
```

### **Service Recovery:**
```bash
# Restart all services
python restart_ultra.py

# Or manual restart
python src_hexagonal/hexagonal_api_enhanced_clean.py
```

## 📊 **SYSTEM STATUS MONITORING**

### **Real-time Status:**
- **Backend:** http://localhost:5002/health
- **Frontend:** http://localhost:5173
- **Dashboard:** http://localhost:5000
- **Prometheus:** http://localhost:8000

### **Key Metrics:**
- **Facts Count:** `/api/facts/count`
- **Governance Status:** `/api/governance/status`
- **LLM Governor:** `/api/governance/llm-status`
- **System Health:** `/health`

## 🎯 **SUCCESS CRITERIA**

### **System Ready When:**
- ✅ Backend responds on port 5002
- ✅ Frontend loads on port 5173
- ✅ WebSocket connection established
- ✅ Database accessible
- ✅ LLM Governor functional
- ✅ Monitoring active

### **Performance Targets:**
- **Backend Response:** <2s
- **Frontend Load:** <3s
- **WebSocket Latency:** <100ms
- **Database Queries:** <500ms

## 🚀 **NEXT STEPS AFTER STARTUP**

1. **Verify all services are running**
2. **Test LLM Governor functionality**
3. **Check monitoring dashboards**
4. **Validate WebSocket communication**
5. **Run comprehensive system tests**

## 📋 **QUICK REFERENCE COMMANDS**

```bash
# Start everything
.\.venv_hexa\Scripts\Activate.ps1
python src_hexagonal/hexagonal_api_enhanced_clean.py

# Test LLM Governor
python test_hybrid_groq.py

# Check status
curl http://localhost:5002/health

# Monitor
curl http://localhost:5000
```

## 🎉 **SESSION READY!**

Your HAK_GAL session is now fully operational with all services running and LLM Governor functionality available. The system is ready for production use with comprehensive monitoring and fallback mechanisms.

**Happy fact processing!** 🚀







