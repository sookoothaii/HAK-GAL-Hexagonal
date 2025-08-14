#!/usr/bin/env python
"""
Check where Transformer models are cached
==========================================
"""

import os
from pathlib import Path

def check_caches():
    """Find where models are actually stored"""
    
    print("="*60)
    print("🔍 CHECKING MODEL CACHE LOCATIONS")
    print("="*60)
    
    # Possible cache locations
    cache_dirs = [
        Path.home() / '.cache' / 'huggingface',
        Path.home() / '.cache' / 'torch' / 'sentence_transformers',
        Path('C:/Users') / os.environ.get('USERNAME', '') / '.cache' / 'huggingface',
        Path('D:/MCP Mods/HAK_GAL_SUITE/.cache'),
        Path('D:/MCP Mods/HAK_GAL_HEXAGONAL/.cache'),
    ]
    
    total_size = 0
    found_models = []
    
    for cache_dir in cache_dirs:
        if cache_dir.exists():
            # Calculate size
            size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
            size_mb = size / (1024*1024)
            
            if size_mb > 10:  # Only show if > 10MB
                print(f"\n📁 Found cache: {cache_dir}")
                print(f"   Size: {size_mb:.1f} MB")
                
                # Check for specific models
                if (cache_dir / 'hub').exists():
                    models = list((cache_dir / 'hub').glob('models--*'))
                    for model in models:
                        model_name = model.name.replace('models--', '').replace('--', '/')
                        found_models.append(model_name)
                        print(f"   ✅ Model: {model_name}")
                
                total_size += size_mb
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total cache size: {total_size:.1f} MB")
    print(f"   Models found: {len(found_models)}")
    
    if 'sentence-transformers/all-MiniLM-L6-v2' in found_models:
        print("   ✅ SentenceTransformer IS cached")
    else:
        print("   ❌ SentenceTransformer NOT cached")
        
    if 'cross-encoder/nli-deberta-v3-base' in found_models:
        print("   ✅ CrossEncoder IS cached")
    else:
        print("   ❌ CrossEncoder NOT cached")
    
    print("\n" + "="*60)
    print("💡 SOLUTION:")
    if total_size < 100:
        print("Models are NOT properly cached - they download every time!")
        print("Run: python download_models_now.py")
    else:
        print("Models ARE cached but loading is slow.")
        print("This is because shared_models.py loads them fresh each time.")
        print("Use the optimized startup script below.")
    print("="*60)

if __name__ == '__main__':
    check_caches()
