---
title: "Hybrid Llm Config"
created: "2025-09-15T00:08:01.041612Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# HAK-GAL Hybrid LLM Configuration Guide
**Version:** 2.0 (August 2025)  
**Status:** PRODUCTION READY

## 🎯 Overview

The HAK-GAL Backend now supports a **Hybrid LLM Strategy** that combines the best of both worlds:
- **Primary**: Google Gemini (cloud, fast ~5s)
- **Fallback**: Ollama (local, reliable ~15s)

## 🚀 Quick Start

### 1. Environment Setup

Create/update `.env` file in `HAK_GAL_SUITE/`:
```bash
# Required for Gemini
GEMINI_API_KEY=your-gemini-api-key-here

# Optional configuration
HAKGAL_PORT=5002
HAKGAL_WRITE_ENABLED=true
```

### 2. Start Services

```bash
# Step 1: Always start Ollama (for fallback)
ollama serve

# Step 2: Activate virtual environment
cd D:\MCP Mods\HAK_GAL_HEXAGONAL
.\.venv_hexa\Scripts\activate

# Step 3: Start the backend
python src_hexagonal\hexagonal_api_enhanced_clean.py
```

## 🔧 Configuration Options

Edit `hexagonal_api_enhanced_clean.py` lines 83-87:

```python
# Hybrid Strategy Configuration
USE_HYBRID_LLM = True           # Enable hybrid (recommended)
USE_LOCAL_OLLAMA_ONLY = False   # Set True for privacy mode
GEMINI_TIMEOUT = 70              # Seconds before fallback
```

### Configuration Modes

| Mode | Settings | Use Case |
|------|----------|----------|
| **Hybrid (Default)** | `USE_HYBRID_LLM=True`<br>`USE_LOCAL_OLLAMA_ONLY=False` | Production with internet |
| **Privacy Mode** | `USE_HYBRID_LLM=False`<br>`USE_LOCAL_OLLAMA_ONLY=True` | Sensitive data, offline |
| **Cloud Only** | `USE_HYBRID_LLM=False`<br>`USE_LOCAL_OLLAMA_ONLY=False` | Testing Gemini |

## 📊 Performance Comparison

| Provider | Response Time | Quality | Availability | Privacy |
|----------|--------------|---------|--------------|---------|
| **Gemini** | ⚡ 5s | ⭐⭐⭐⭐⭐ | Internet required | Cloud |
| **Ollama** | 🐢 15s | ⭐⭐⭐⭐ | Always available | 100% Local |

## 🔄 Fallback Triggers

Ollama will be used when:
1. ❌ Gemini API key not configured
2. ❌ Network/Internet unavailable
3. ❌ Gemini API error
4. ❌ Gemini timeout (>70 seconds)
5. ❌ Gemini service down

## 🔍 Response Structure

The API response now includes provider information:

```json
{
  "status": "success",
  "explanation": "...",
  "suggested_facts": [...],
  "llm_provider": "Gemini",  // or "Ollama"
  "response_time": "~5s"      // or "~15s"
}
```

## 🔒 Privacy Considerations

- **Sensitive Data**: Use `USE_LOCAL_OLLAMA_ONLY=True`
- **Development**: Can use Ollama for cost-free testing
- **Production**: Hybrid mode for best user experience
- **Compliance**: Ollama ensures GDPR/DSGVO compliance

## 🐛 Troubleshooting

### Gemini Not Working
```bash
# Check API key
echo %GEMINI_API_KEY%

# Test connectivity
curl https://generativelanguage.googleapis.com/v1/models
```

### Ollama Not Available
```bash
# Check if Ollama is running
ollama list

# Start Ollama
ollama serve

# Pull required model
ollama pull qwen2.5:7b
```

### Both Providers Failing
1. Check console output for specific errors
2. Verify `.env` file location and content
3. Ensure network connectivity
4. Check firewall settings

## 📈 Monitoring

Watch the console for LLM selection:
```
[MultiLLM] Trying Gemini (1/2)...
[MultiLLM] Success with Gemini
```

Or in fallback case:
```
[MultiLLM] Trying Gemini (1/2)...
[Gemini] Failed: [error]. Falling back to Ollama...
[LLM] Success with Ollama
```

## 🎯 Best Practices

1. **Always run Ollama** even when using Gemini primary
2. **Monitor API costs** for Gemini usage
3. **Test fallback** regularly by disabling internet
4. **Log provider usage** for optimization
5. **Update models** periodically (`ollama pull`)

## 📝 Testing the Hybrid System

```bash
# Test with curl
curl -X POST http://localhost:5002/api/llm/get-explanation \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What is machine learning?\"}"

# Check response for llm_provider field
```

## 🚀 Future Enhancements

- [ ] Add more fallback providers (Claude, OpenAI)
- [ ] Implement provider rotation for load balancing
- [ ] Add cost tracking for cloud providers
- [ ] Cache responses to reduce API calls
- [ ] Add provider health checks

---

**Updated:** August 24, 2025  
**Maintainer:** HAK-GAL Team  
**File:** `src_hexagonal/hexagonal_api_enhanced_clean.py`
