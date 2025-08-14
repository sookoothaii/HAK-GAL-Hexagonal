#!/usr/bin/env python3
"""
HAK-GAL Hexagonal - Main Entry Point
=====================================
Startet die Hexagonal API auf Port 5001
"""

import sys
from pathlib import Path

# Add src_hexagonal to path for all imports
sys.path.insert(0, str(Path(__file__).parent / "src_hexagonal"))

def main():
    """Main Entry Point"""
    print("\n" + "=" * 60)
    print("HAK-GAL HEXAGONAL ARCHITECTURE - STARTUP")
    print("=" * 60)
    
    # Check if we should use legacy or sqlite
    use_legacy = True  # Default to legacy
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--sqlite':
            use_legacy = False
            print("📦 Mode: SQLite (Development Database)")
        elif sys.argv[1] == '--help':
            print("Usage: python start_hexagonal.py [--legacy|--sqlite]")
            print("  --legacy : Use Original HAK-GAL System (default)")
            print("  --sqlite : Use SQLite Development Database")
            sys.exit(0)
        else:
            print("🔗 Mode: Legacy (Original HAK-GAL System)")
    else:
        print("🔗 Mode: Legacy (Original HAK-GAL System)")
    
    # Import and start API
    try:
        # Now import after path is set
        from hexagonal_api import create_app
        
        api = create_app(use_legacy=use_legacy)
        api.run(
            host='127.0.0.1',
            port=5001,
            debug=True
        )
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nMake sure you have installed dependencies:")
        print("  pip install flask flask-cors")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Startup Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
