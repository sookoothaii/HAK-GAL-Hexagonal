#!/usr/bin/env python3
"""
CUDA Status Check für HAK-GAL Hexagonal
Nach HAK/GAL Verfassung Artikel 6: Empirische Validierung
"""

import torch
import sys
from pathlib import Path

def check_cuda_status():
    """Empirische CUDA-Status-Prüfung"""
    
    print("=" * 60)
    print("HAK-GAL HEXAGONAL: CUDA Status Diagnose")
    print("=" * 60)
    
    # 1. PyTorch Version
    print(f"\n📊 PyTorch Version: {torch.__version__}")
    
    # 2. CUDA Verfügbarkeit
    cuda_available = torch.cuda.is_available()
    print(f"\n🖥️ CUDA Available: {cuda_available}")
    
    if cuda_available:
        # 3. CUDA Version
        print(f"🔧 CUDA Version: {torch.version.cuda}")
        
        # 4. GPU Count
        gpu_count = torch.cuda.device_count()
        print(f"🎮 GPU Count: {gpu_count}")
        
        # 5. GPU Details
        for i in range(gpu_count):
            gpu_name = torch.cuda.get_device_name(i)
            gpu_memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)
            print(f"\n  GPU {i}: {gpu_name}")
            print(f"  Memory: {gpu_memory:.2f} GB")
            
            # Current Memory Usage
            if torch.cuda.is_available():
                torch.cuda.set_device(i)
                allocated = torch.cuda.memory_allocated(i) / (1024**2)
                reserved = torch.cuda.memory_reserved(i) / (1024**2)
                print(f"  Allocated: {allocated:.2f} MB")
                print(f"  Reserved: {reserved:.2f} MB")
    else:
        print("\n❌ CUDA ist NICHT verfügbar!")
        print("\nMögliche Gründe:")
        print("1. Keine NVIDIA GPU vorhanden")
        print("2. CUDA-Treiber nicht installiert")
        print("3. PyTorch ohne CUDA-Support installiert")
        
        # Check PyTorch Build
        print(f"\n🔍 PyTorch Build Info:")
        print(f"  Has CUDA: {torch.backends.cuda.is_built()}")
        print(f"  Has CUDNN: {torch.backends.cudnn.is_available()}")
        
    # 6. Test Tensor Creation
    print("\n🧪 Test Tensor Creation:")
    try:
        if cuda_available:
            test_tensor = torch.randn(100, 100).cuda()
            print(f"  ✅ CUDA Tensor erfolgreich erstellt")
            print(f"  Device: {test_tensor.device}")
            del test_tensor
            torch.cuda.empty_cache()
        else:
            test_tensor = torch.randn(100, 100)
            print(f"  ⚠️ CPU Tensor erstellt (CUDA nicht verfügbar)")
            print(f"  Device: {test_tensor.device}")
    except Exception as e:
        print(f"  ❌ Fehler beim Tensor-Test: {e}")
    
    # 7. Empfehlungen
    print("\n📝 Empfehlungen:")
    if cuda_available:
        print("✅ CUDA ist verfügbar und funktioniert!")
        print("→ Aktiviere CUDA in der unified_hrm_api.py")
    else:
        print("⚠️ CUDA ist nicht verfügbar.")
        print("→ Installiere PyTorch mit CUDA Support:")
        print("  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
    
    return cuda_available

if __name__ == "__main__":
    cuda_available = check_cuda_status()
    sys.exit(0 if cuda_available else 1)
