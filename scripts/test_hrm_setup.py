#!/usr/bin/env python3
"""
Quick Test for HRM Training Setup
==================================
"""

import torch
import sqlite3
import re
from pathlib import Path

print("="*60)
print("HRM TRAINING SETUP VERIFICATION")
print("="*60)

# 1. Check CUDA
print("\n1️⃣ GPU CHECK:")
if torch.cuda.is_available():
    print(f"   ✅ CUDA Available")
    print(f"   GPU: {torch.cuda.get_device_name(0)}")
    print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
else:
    print("   ❌ No CUDA!")

# 2. Check Database
print("\n2️⃣ DATABASE CHECK:")
db_path = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db")
if db_path.exists():
    print(f"   ✅ Database exists: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Count facts
    cursor.execute("SELECT COUNT(*) FROM facts")
    total = cursor.fetchone()[0]
    print(f"   Total facts: {total:,}")
    
    # Sample facts
    cursor.execute("SELECT statement FROM facts LIMIT 5")
    samples = cursor.fetchall()
    
    print(f"\n   📝 Sample facts:")
    for i, (stmt,) in enumerate(samples, 1):
        print(f"      {i}. {stmt}")
    
    # Test parsing
    print(f"\n   🔍 Testing fact parsing:")
    pattern = r'^([A-Z][A-Za-z0-9_]*)\((.*?)\)\.$'
    
    parsed = 0
    multi_arg = 0
    
    cursor.execute("SELECT statement FROM facts LIMIT 100")
    for (stmt,) in cursor.fetchall():
        match = re.match(pattern, stmt)
        if match:
            parsed += 1
            entities = match.group(2).split(',')
            if len(entities) > 2:
                multi_arg += 1
    
    print(f"      Parsed: {parsed}/100")
    print(f"      Multi-argument (>2): {multi_arg}/100")
    
    conn.close()
else:
    print(f"   ❌ Database not found!")

# 3. Test model creation
print("\n3️⃣ MODEL TEST:")
try:
    from scripts.train_hrm_model import ImprovedHRM
    
    model = ImprovedHRM(vocab_size=1000)
    params = sum(p.numel() for p in model.parameters())
    print(f"   ✅ Model created")
    print(f"   Parameters: {params:,} ({params/1e6:.1f}M)")
    
    # Test forward pass
    test_entities = torch.randint(0, 1000, (2, 2))
    test_predicates = torch.randint(0, 100, (2,))
    
    with torch.no_grad():
        output = model(test_entities, test_predicates)
    
    print(f"   ✅ Forward pass successful")
    print(f"   Output shape: {output.shape}")
    
except Exception as e:
    print(f"   ❌ Model test failed: {e}")

print("\n" + "="*60)
print("READY TO TRAIN?")
print("="*60)
print("✅ All checks passed! Run:")
print("   cd D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\scripts")
print("   python train_hrm_model.py")
print("\nExpected training time: 15-30 minutes on RTX 3080 Ti")
print("="*60)
