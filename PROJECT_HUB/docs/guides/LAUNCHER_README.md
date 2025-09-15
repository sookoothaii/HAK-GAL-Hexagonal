---
title: "Launcher Readme"
created: "2025-09-15T00:08:01.013317Z"
author: "system-cleanup"
topics: ["guides"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# 🚀 HAK-GAL Launch Scripts

## Quick Start

### Option 1: PowerShell (Recommended)
```powershell
# Complete launcher with health checks
.\START_ALL_SERVICES.ps1

# Or quick minimal launcher
.\QUICK_START.ps1
```

### Option 2: Batch File
```cmd
# For systems with PowerShell restrictions
START_ALL_SERVICES.bat
```

### Stop All Services
```powershell
.\STOP_ALL_SERVICES.ps1
```

---

## 📋 Scripts Overview

| Script | Purpose | Features |
|--------|---------|----------|
| **START_ALL_SERVICES.ps1** | Full launcher | Health checks, port clearing, auto-browser |
| **QUICK_START.ps1** | Minimal launcher | Fast, simple, no checks |
| **STOP_ALL_SERVICES.ps1** | Stop everything | Clean shutdown of all services |
| **START_ALL_SERVICES.bat** | Batch alternative | For restricted systems |

---

## 🔧 What Gets Started

### Core Services
1. **Port 5002** - HAK-GAL Hexagonal API
   - Main API with Ollama integration
   - Knowledge Base management
   - Auto-add facts feature

2. **Port 5173** - Frontend (npm run dev)
   - React/Vue frontend
   - Visual interface for HAK-GAL

3. **Port 8088** - Additional Service
   - Custom service (if configured)
   - API extensions

### Optional Services
4. **Port 5001** - Governor Service
   - Background learning
   - Automated fact generation

5. **Port 11434** - Ollama
   - Local LLM inference
   - Phi3 model

---

## ⚙️ Configuration

### PowerShell Execution Policy
If you get execution errors:
```powershell
# Allow script execution (run as Admin)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or bypass for single run
powershell -ExecutionPolicy Bypass -File .\START_ALL_SERVICES.ps1
```

### Custom Port Configuration
Edit the scripts to change ports:
```powershell
# In START_ALL_SERVICES.ps1
$ports = @(5002, 5173, 8088, 5001, 5000)  # Modify as needed
```

### Skip Ollama Check
```powershell
.\START_ALL_SERVICES.ps1 -NoOllama
```

---

## 🔍 Troubleshooting

### Port Already in Use
The scripts automatically kill processes on required ports. If issues persist:
```powershell
# Manual port cleanup
netstat -ano | findstr :5002
taskkill /PID <process_id> /F
```

### Frontend Not Starting
1. Check if `frontend` directory exists
2. Run `npm install` in frontend directory
3. Check `package.json` for correct scripts

### Service on 8088 Not Found
Create `service_8088.py` in root directory or configure path in script.

### Virtual Environment Issues
Scripts auto-detect `.venv_hexa` or `venv`. If using different name:
```powershell
# Edit in script
$PYTHON = ".\your_venv\Scripts\python.exe"
```

---

## 📊 Health Checks

The main launcher performs automatic health checks:
- ✅ Python environment
- ✅ NPM availability
- ✅ Ollama status
- ✅ Port availability
- ✅ Service responsiveness

---

## 💡 Tips

### Development Workflow
```powershell
# Morning startup
.\START_ALL_SERVICES.ps1

# Quick restart during development
.\STOP_ALL_SERVICES.ps1
.\QUICK_START.ps1

# End of day
.\STOP_ALL_SERVICES.ps1
```

### Production Deployment
Consider using:
- Windows Services for auto-start
- Process managers (PM2, Supervisor)
- Docker containers

### Custom Services
Add your own services by creating:
- `service_8088.py` for port 8088
- Modify scripts to add more ports

---

## 🎯 Quick Commands

```powershell
# Start everything
.\START_ALL_SERVICES.ps1

# Stop everything
.\STOP_ALL_SERVICES.ps1

# Check what's running
netstat -an | findstr "5002 5173 8088"

# Open browser manually
start http://localhost:5173
```

---

## 📝 Notes

- Each service runs in its own terminal window
- Closing the launcher window does NOT stop services
- Services continue running until explicitly stopped
- Logs are visible in each service window

---

**Happy Launching! 🚀**
