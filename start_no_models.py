#!/usr/bin/env python
"""
Start Backend WITHOUT Transformer Models
=========================================
Clean solution - no ML models, just core functionality
"""

import sys
import os
from pathlib import Path

# Disable ALL ML models
os.environ['DISABLE_SENTENCE_TRANSFORMERS'] = '1'
os.environ['DISABLE_CROSS_ENCODER'] = '1'
os.environ['DISABLE_ML_MODELS'] = '1'

# Add paths
sys.path.insert(0, str(Path(__file__).parent / 'src_hexagonal'))

def patch_shared_models():
    """Monkey-patch to prevent model loading"""
    import sys
    
    # Create mock module
    class MockSentenceTransformer:
        def __init__(self, *args, **kwargs):
            pass
        def encode(self, *args, **kwargs):
            return [[0.5] * 384]  # Dummy embeddings
    
    class MockCrossEncoder:
        def __init__(self, *args, **kwargs):
            pass
        def predict(self, *args, **kwargs):
            return [0.5]
    
    # Inject mocks
    sys.modules['sentence_transformers'] = type(sys)('sentence_transformers')
    sys.modules['sentence_transformers'].SentenceTransformer = MockSentenceTransformer
    sys.modules['sentence_transformers'].CrossEncoder = MockCrossEncoder

def start_without_models():
    """Start backend without ML models"""
    
    print("="*60)
    print("🚀 HAK-GAL HEXAGONAL - NO ML MODELS")
    print("="*60)
    print("[INFO] Running WITHOUT transformer models")
    print("[INFO] Semantic search DISABLED")
    print("[INFO] Using k_assistant_dev.db (3079 facts)")
    print("[INFO] Core functionality only")
    print("="*60)
    
    # Patch before any imports
    patch_shared_models()
    
    # Set correct database
    os.environ['HAK_GAL_DB_URI'] = 'sqlite:///D:/MCP Mods/HAK_GAL_HEXAGONAL/k_assistant_dev.db'
    
    # Import and start
    from hexagonal_api_enhanced import HexagonalAPI
    
    api = HexagonalAPI(
        use_legacy=True,
        enable_websocket=True,
        enable_governor=True,
        enable_sentry=False
    )
    
    # Run
    api.run(host='127.0.0.1', port=5001, debug=True)

if __name__ == '__main__':
    start_without_models()
