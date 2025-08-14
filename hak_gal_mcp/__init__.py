#!/usr/bin/env python3
"""
HAK_GAL MCP Module
Model Context Protocol server for HAK_GAL Knowledge Base
"""

__version__ = "1.0.0"
__author__ = "HAK_GAL Research Team"

# Module initialization
import sys
import os

# Ensure parent directory is in path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
