#!/usr/bin/env python3
"""
Check CUDA in Hexagonal Environment
"""

import torch
import sys

print("="*60)
print("HEXAGONAL ENVIRONMENT CUDA CHECK")
print("="*60)
print(f"Python: {sys.executable}")
print(f"PyTorch Version: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA Version: {torch.version.cuda}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
else:
    print("\n❌ CUDA NOT AVAILABLE IN THIS ENVIRONMENT!")
    print("\nPossible reasons:")
    print("1. PyTorch installed without CUDA support")
    print("2. Different PyTorch version")
    
    print(f"\nPyTorch Build Info:")
    print(f"  Has CUDA: {torch.backends.cuda.is_built()}")
    print(f"  Has CUDNN: {torch.backends.cudnn.is_available()}")
    
    print("\n🔧 FIX: Install PyTorch with CUDA:")
    print("pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")

print("="*60)
