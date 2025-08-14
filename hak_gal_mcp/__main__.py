#!/usr/bin/env python3
"""
__main__.py for hak_gal_mcp module
Allows running as: python -m hak_gal_mcp
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import and run the fixed MCP server
from hak_gal_mcp_fixed import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
