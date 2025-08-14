#!/usr/bin/env python
"""
Start Hexagonal API WITHOUT Heavy ML Models
============================================
Lightweight version for development/testing
"""

import sys
import os
from pathlib import Path

# Disable transformer models
os.environ['DISABLE_TRANSFORMERS'] = 'true'
os.environ['DISABLE_SENTENCE_TRANSFORMERS'] = 'true'

# Add src_hexagonal to path
sys.path.insert(0, str(Path(__file__).parent / 'src_hexagonal'))

from hexagonal_api_enhanced import HexagonalAPI

def start_lightweight_backend():
    """Start the backend without heavy ML models"""
    
    print("=" * 60)
    print("🚀 HAK-GAL HEXAGONAL - Lightweight Mode")
    print("=" * 60)
    print("[INFO] Running WITHOUT transformer models")
    print("[INFO] Using SQLite database")
    print("[INFO] Semantic search disabled")
    print("=" * 60)
    
    # Create API with SQLite
    api = HexagonalAPI(
        use_legacy=False,  # SQLite
        enable_websocket=True,
        enable_governor=True,
        enable_sentry=False  # Disable Sentry for lightweight mode
    )
    
    # Run on port 5001
    api.run(host='127.0.0.1', port=5001, debug=True)

if __name__ == '__main__':
    start_lightweight_backend()
