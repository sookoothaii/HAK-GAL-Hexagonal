#!/usr/bin/env python
"""
Pre-download Transformer Models
================================
Run this once to download models before starting the backend
"""

import os
import sys

def download_models():
    """Download required transformer models"""
    
    print("=" * 60)
    print("📥 Downloading Transformer Models")
    print("=" * 60)
    print("This may take a few minutes on first run...")
    print()
    
    try:
        # Set offline mode to false to allow downloads
        os.environ['TRANSFORMERS_OFFLINE'] = '0'
        os.environ['HF_HUB_OFFLINE'] = '0'
        
        # Try to download SentenceTransformer model
        print("1. Downloading SentenceTransformer model...")
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("   ✅ SentenceTransformer model downloaded")
        
        # Try to download CrossEncoder model  
        print("\n2. Downloading CrossEncoder model...")
        from sentence_transformers import CrossEncoder
        cross_encoder = CrossEncoder('cross-encoder/nli-deberta-v3-base')
        print("   ✅ CrossEncoder model downloaded")
        
        print("\n" + "=" * 60)
        print("✅ All models downloaded successfully!")
        print("You can now start the backend without download delays")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error downloading models: {e}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Try setting proxy if behind firewall:")
        print("   set HTTP_PROXY=http://your-proxy:port")
        print("   set HTTPS_PROXY=http://your-proxy:port")
        print("3. Or download models manually and place in cache")
        return False
    
    return True

if __name__ == '__main__':
    success = download_models()
    sys.exit(0 if success else 1)
