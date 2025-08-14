#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MIGRATION STEP 1: Port Shared Models to HEXAGONAL
==================================================
Standalone, optimized version without HAK_GAL_SUITE dependency
"""

import os
import sys
import shutil
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def migrate_shared_models():
    """Create standalone shared_models in HEXAGONAL"""
    
    print("="*60)
    print("[STEP 1] MIGRATING SHARED MODELS TO HEXAGONAL")
    print("="*60)
    
    # Create new shared models module
    shared_models_code = '''"""
Shared Models for HEXAGONAL - Standalone Version
================================================
No dependency on HAK_GAL_SUITE!
"""

import os
import torch
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class SharedModels:
    """Singleton for ML models with lazy loading"""
    
    _instance = None
    _sentence_model = None
    _cross_encoder = None
    _device = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = False
            self._setup_device()
    
    def _setup_device(self):
        """Setup CUDA if available"""
        if torch.cuda.is_available():
            self._device = torch.device('cuda:0')
            gpu_name = torch.cuda.get_device_name(0)
            memory_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
            logger.info(f"[OK] CUDA Available: {gpu_name} ({memory_gb:.2f} GB)")
        else:
            self._device = torch.device('cpu')
            logger.info("[INFO] Using CPU (CUDA not available)")
    
    @property
    def sentence_model(self):
        """Lazy load sentence transformer"""
        if self._sentence_model is None:
            try:
                logger.info("[MODELS] Loading SentenceTransformer...")
                from sentence_transformers import SentenceTransformer
                
                # Use local cache
                cache_dir = Path(__file__).parent.parent / '.cache' / 'models'
                cache_dir.mkdir(parents=True, exist_ok=True)
                os.environ['SENTENCE_TRANSFORMERS_HOME'] = str(cache_dir)
                
                self._sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
                self._sentence_model = self._sentence_model.to(self._device)
                logger.info("[MODELS] SentenceTransformer ready")
            except ImportError:
                logger.warning("[MODELS] SentenceTransformer not available")
                return None
        return self._sentence_model
    
    @property
    def cross_encoder(self):
        """Lazy load cross encoder"""
        if self._cross_encoder is None:
            try:
                logger.info("[MODELS] Loading CrossEncoder...")
                from sentence_transformers import CrossEncoder
                
                self._cross_encoder = CrossEncoder('cross-encoder/nli-deberta-v3-base')
                if self._device.type == 'cuda':
                    self._cross_encoder.model = self._cross_encoder.model.to(self._device)
                logger.info("[MODELS] CrossEncoder ready")
            except ImportError:
                logger.warning("[MODELS] CrossEncoder not available")
                return None
        return self._cross_encoder
    
    def encode_text(self, text: str):
        """Encode text with sentence transformer"""
        if self.sentence_model:
            return self.sentence_model.encode(text)
        else:
            # Fallback: simple hash-based encoding
            import hashlib
            hash_val = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
            return [float(hash_val % 1000) / 1000.0] * 384
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute similarity between two texts"""
        if self.cross_encoder:
            return float(self.cross_encoder.predict([[text1, text2]])[0])
        else:
            # Fallback: simple string similarity
            from difflib import SequenceMatcher
            return SequenceMatcher(None, text1, text2).ratio()

# Global instance
shared_models = SharedModels()

# Export for compatibility
def get_sentence_model():
    return shared_models.sentence_model

def get_cross_encoder():
    return shared_models.cross_encoder
'''
    
    # Save to HEXAGONAL
    output_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/src_hexagonal/core/ml/shared_models.py")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(shared_models_code)
    
    print(f"[OK] Created: {output_path}")
    
    # Create __init__.py
    init_path = output_path.parent / "__init__.py"
    with open(init_path, 'w') as f:
        f.write('"""ML Models Module"""')
    
    print(f"[OK] Created: {init_path}")
    
    print("\n" + "="*60)
    print("[SUCCESS] SHARED MODELS MIGRATED!")
    print("Now independent from HAK_GAL_SUITE")
    print("="*60)

if __name__ == '__main__':
    try:
        migrate_shared_models()
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        sys.exit(1)
