#!/usr/bin/env python
"""
Pre-Download ALL Required Models
=================================
Run this ONCE to get all models, then backend starts instantly
"""

import os
import sys

def download_all_models():
    """Download all required models BEFORE starting backend"""
    
    print("="*60)
    print("📥 DOWNLOADING ALL REQUIRED MODELS")
    print("="*60)
    print("This will take 2-5 minutes on first run...")
    print("After this, backend will start instantly!\n")
    
    # Force online mode for downloads
    os.environ['TRANSFORMERS_OFFLINE'] = '0'
    os.environ['HF_HUB_OFFLINE'] = '0'
    
    try:
        # 1. SentenceTransformer
        print("1/2 Downloading SentenceTransformer (all-MiniLM-L6-v2)...")
        print("    Size: ~90 MB")
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("    ✅ SentenceTransformer ready!\n")
        
        # 2. Cross-Encoder
        print("2/2 Downloading Cross-Encoder (nli-deberta-v3-base)...")
        print("    Size: ~760 MB")
        from sentence_transformers import CrossEncoder
        cross_encoder = CrossEncoder('cross-encoder/nli-deberta-v3-base')
        print("    ✅ Cross-Encoder ready!\n")
        
        print("="*60)
        print("✅ ALL MODELS DOWNLOADED SUCCESSFULLY!")
        print("="*60)
        print("\nNow you can start the backend normally:")
        print("  .\\start_backend_working.bat")
        print("\nThe models are cached and will load instantly!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error downloading models: {e}")
        print("\nTroubleshooting:")
        print("1. Check internet connection")
        print("2. Check if behind proxy/firewall")
        print("3. Try again or use Option 2 (no models)")
        return False

if __name__ == '__main__':
    success = download_all_models()
    sys.exit(0 if success else 1)
