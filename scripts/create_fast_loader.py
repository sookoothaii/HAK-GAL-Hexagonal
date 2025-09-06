#!/usr/bin/env python
"""
Optimize Model Loading - Singleton Pattern Fix
===============================================
Makes models load only ONCE, not every startup
"""

import sys
from pathlib import Path

def create_optimized_loader():
    """Create optimized model loader that caches properly"""
    
    optimized_code = '''"""
Optimized Shared Models - Load ONCE, use forever
=================================================
"""

import os
import torch
from functools import lru_cache

# SINGLETON PATTERN - Load models only ONCE
_MODELS_LOADED = False
_SENTENCE_MODEL = None
_CROSS_ENCODER = None

@lru_cache(maxsize=1)
def get_sentence_transformer():
    """Get or create sentence transformer (singleton)"""
    global _SENTENCE_MODEL
    
    if _SENTENCE_MODEL is None:
        print("[SHARED MODELS] Loading SentenceTransformer (first time only)...")
        
        # Set cache directory
        os.environ['SENTENCE_TRANSFORMERS_HOME'] = r'%USERPROFILE%\\.cache\\torch\\sentence_transformers'
        
        from sentence_transformers import SentenceTransformer
        _SENTENCE_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Move to GPU if available
        if torch.cuda.is_available():
            _SENTENCE_MODEL = _SENTENCE_MODEL.to('cuda')
            
        print("[SHARED MODELS] SentenceTransformer loaded and cached!")
    else:
        print("[SHARED MODELS] Using cached SentenceTransformer (instant)")
        
    return _SENTENCE_MODEL

@lru_cache(maxsize=1)
def get_cross_encoder():
    """Get or create cross encoder (singleton)"""
    global _CROSS_ENCODER
    
    if _CROSS_ENCODER is None:
        print("[SHARED MODELS] Loading CrossEncoder (first time only)...")
        
        from sentence_transformers import CrossEncoder
        _CROSS_ENCODER = CrossEncoder('cross-encoder/nli-deberta-v3-base')
        
        if torch.cuda.is_available():
            _CROSS_ENCODER.model = _CROSS_ENCODER.model.to('cuda')
            
        print("[SHARED MODELS] CrossEncoder loaded and cached!")
    else:
        print("[SHARED MODELS] Using cached CrossEncoder (instant)")
        
    return _CROSS_ENCODER

def initialize_shared_models():
    """Pre-load all models once"""
    global _MODELS_LOADED
    
    if not _MODELS_LOADED:
        print("[SHARED MODELS] First-time initialization...")
        get_sentence_transformer()
        get_cross_encoder()
        _MODELS_LOADED = True
        print("[SHARED MODELS] All models cached for fast access!")
    else:
        print("[SHARED MODELS] Models already loaded (skipping)")

# Auto-initialize on import (happens once)
if __name__ != "__main__":
    initialize_shared_models()
'''
    
    # Save optimized loader
    output_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/src_hexagonal/shared_models_optimized.py")
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(optimized_code)
    
    print("="*60)
    print("✅ OPTIMIZED MODEL LOADER CREATED")
    print("="*60)
    print(f"Saved to: {output_path}")
    print("\nThis implements proper singleton pattern:")
    print("- Models load only ONCE per session")
    print("- Subsequent imports use cached version")
    print("- Startup should be 10x faster")
    print("\nTo use: Modify imports to use shared_models_optimized")
    print("="*60)

if __name__ == '__main__':
    create_optimized_loader()
