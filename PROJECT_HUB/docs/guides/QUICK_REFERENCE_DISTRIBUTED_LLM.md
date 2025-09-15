---
title: "Quick Reference Distributed Llm"
created: "2025-09-15T00:08:01.017315Z"
author: "system-cleanup"
topics: ["guides"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# QUICK REFERENCE CARD - Distributed LLM Setup
## 2x Lenovo Legion (32GB VRAM Total)

---

## 🚀 SCHNELLSTART

### Laptop 1 (AMD - RPC Server):
```bash
./rpc-server -H 0.0.0.0 -p 50052
```

### Laptop 2 (Intel - Main Server):
```bash
./llama-server \
  --model deepseek-v3-q4_k_m.gguf \
  --rpc 10.0.0.1:50052 \
  --n-gpu-layers 35 \
  --ctx-size 8192 \
  --port 8080
```

---

## 📊 MODELL-ÜBERSICHT

| Modell | Q-Type | VRAM | Speed | Befehl |
|--------|--------|------|-------|--------|
| **DeepSeek-V3** | Q4_K_M | 27GB | 4-6 t/s | `--n-gpu-layers 35` |
| **Llama 3.3 70B** | Q3_K_S | 26GB | 3-5 t/s | `--n-gpu-layers 70` |
| **Qwen 2.5 72B** | Q3_K_M | 28GB | 2-4 t/s | `--n-gpu-layers 65` |
| **Mixtral 8x7B** | Q6_K | 26GB | 6-8 t/s | `--n-gpu-layers 32` |

---

## 🔧 VRAM OPTIMIERUNG

```bash
# Maximale Performance (27GB)
--n-gpu-layers 35 --ctx-size 8192

# Mehr Context (25GB)
--n-gpu-layers 30 --ctx-size 16384

# Stabiler Betrieb (24GB)
--n-gpu-layers 30 --ctx-size 8192 --n-batch 256
```

### Cache-Optimierung:
```bash
--cache-type-k q4_0  # Spart 50% KV-Cache
--cache-type-v q4_0
--flash-attn         # Spart 10-15% VRAM
```

---

## 🌐 NETZWERK-SETUP

### Direkte Ethernet-Verbindung:
```bash
# Laptop 1 (10.0.0.1)
sudo ip addr add 10.0.0.1/24 dev eth0
sudo ip link set eth0 up

# Laptop 2 (10.0.0.2)
sudo ip addr add 10.0.0.2/24 dev eth0
sudo ip link set eth0 up

# Test
ping 10.0.0.1
iperf3 -s         # Server
iperf3 -c 10.0.0.1  # Client
```

---

## 🔍 MONITORING

### GPU Status:
```bash
# Live VRAM
watch -n 1 nvidia-smi

# Detailed
nvidia-smi dmon -s mu

# Both GPUs (SSH)
ssh laptop1 nvidia-smi & nvidia-smi
```

### Performance Test:
```bash
curl -X POST http://localhost:8080/completion \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test", "n_predict": 100}'
```

---

## 🛠️ TROUBLESHOOTING

| Problem | Lösung |
|---------|--------|
| **OOM** | `--n-gpu-layers 25` reduzieren |
| **Slow** | Ethernet prüfen, `--flash-attn` |
| **No Connection** | Firewall: `sudo ufw allow 50052` |
| **Crash** | `--ctx-size 4096` reduzieren |

---

## 📝 LAYER SPLIT FORMELN

```python
# Optimale Verteilung berechnen
total_layers = 80  # Llama 70B
vram_laptop1 = 16  # GB
vram_laptop2 = 16  # GB

# Proportional
layers_laptop1 = int(total_layers * vram_laptop1 / (vram_laptop1 + vram_laptop2))
layers_laptop2 = total_layers - layers_laptop1

# Asymmetrisch (Intel stärker)
layers_laptop1 = 35  # AMD
layers_laptop2 = 45  # Intel
```

---

## 🎯 PERFORMANCE TARGETS

| Metric | Gut | Optimal | Maximum |
|--------|-----|---------|---------|
| **Load Time** | <2min | <1min | <30s |
| **First Token** | <10s | <5s | <2s |
| **Tokens/sec** | >2 | >4 | >6 |
| **VRAM Usage** | 70% | 85% | 95% |

---

## 💻 API USAGE

### Python:
```python
import openai
client = openai.OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="not-needed"
)
response = client.chat.completions.create(
    model="local-model",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### cURL:
```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local",
    "messages": [{"role": "user", "content": "Hi"}]
  }'
```

---

## 📊 BENCHMARK COMMANDS

```bash
# Speed Test
time ./llama-cli -m model.gguf -p "Test" -n 100

# Quality Test
./perplexity -m model.gguf -f wiki.test.raw

# Stress Test
for i in {1..10}; do
  curl http://localhost:8080/completion \
    -d '{"prompt": "Test '$i'"}' &
done
```

---

## 🔐 SECURITY

```bash
# Firewall
sudo ufw allow from 10.0.0.0/24

# SSH Tunnel
ssh -L 8080:localhost:8080 laptop2

# Basic Auth (nginx)
htpasswd -c /etc/nginx/.htpasswd user
```

---

## 📦 MODEL DOWNLOADS

```bash
# DeepSeek-V3
wget https://huggingface.co/deepseek-ai/DeepSeek-V3-GGUF/resolve/main/deepseek-v3-q4_k_m.gguf

# Llama 3.3 70B
wget https://huggingface.co/bartowski/Llama-3.3-70B-Instruct-GGUF/resolve/main/Llama-3.3-70B-Instruct-Q3_K_S.gguf

# Qwen 2.5 72B
wget https://huggingface.co/Qwen/Qwen2.5-72B-GGUF/resolve/main/qwen2.5-72b-instruct-q3_k_m.gguf
```

---

## ⚡ POWER SETTINGS

```bash
# Max Performance
sudo nvidia-smi -pm 1
sudo nvidia-smi -pl 150  # RTX 3080 Ti

# CPU Governor
sudo cpupower frequency-set -g performance

# Disable Boost (if thermal issues)
echo 0 | sudo tee /sys/devices/system/cpu/cpufreq/boost
```

---

## 📈 ERWEITERUNGEN

### Mehr VRAM benötigt?
1. Dritter Laptop hinzufügen
2. Cloud-GPU als dritten Node
3. CPU/RAM Offloading erhöhen

### Schnellere Verbindung?
1. 10G Ethernet Adapter
2. Thunderbolt 4 Bridge
3. InfiniBand (overkill)

---

## 🆘 NOTFALL-COMMANDS

```bash
# Kill all
pkill -f llama
pkill -f rpc-server

# Clear VRAM
nvidia-smi --gpu-reset

# Emergency shutdown
sudo shutdown -h now
```

---

**Version:** 1.0 | **Updated:** 2025 | **Projekt:** HAK_GAL