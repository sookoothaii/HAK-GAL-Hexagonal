#!/usr/bin/env python3
"""
HAK_GAL API Wrapper with DNS Fix
"""
import sys
import os

# Apply DNS patch first
try:
    import dns_patch
except:
    print("[WARNING] DNS patch not applied")

# Start original application
if __name__ == "__main__":
    import hexagonal_api_enhanced_clean
    hexagonal_api_enhanced_clean.main()
