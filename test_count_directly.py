#!/usr/bin/env python3
"""
Direct Test of Count Method Fix
Nach HAK/GAL Verfassung Artikel 6: Empirische Validierung
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "src_hexagonal"))
sys.path.insert(0, r"D:\MCP Mods\HAK_GAL_SUITE\src")

def test_count_directly():
    """Test the count method directly without API"""
    
    print("=" * 60)
    print("🔍 DIRECT COUNT METHOD TEST")
    print("=" * 60)
    
    try:
        # Import the repository
        from adapters.legacy_adapters import LegacyFactRepository
        
        print("\n1. Creating LegacyFactRepository instance...")
        repo = LegacyFactRepository()
        print("   ✅ Repository created")
        
        print("\n2. Testing count() method...")
        count = repo.count()
        print(f"   Result: {count}")
        
        if count == 3080:
            print("   ✅ SUCCESS: Count returns 3080!")
        elif count == 0:
            print("   ❌ FAILURE: Count returns 0")
            print("\n   Debugging count() internals...")
            
            # Try to debug what's happening
            if hasattr(repo, 'legacy') and repo.legacy:
                print("   - legacy proxy exists")
                
                if hasattr(repo.legacy, 'k_assistant'):
                    print("   - k_assistant exists")
                    
                    # Try direct DB query
                    if hasattr(repo.legacy.k_assistant, 'db_session'):
                        print("   - db_session exists")
                        try:
                            from sqlalchemy import text
                            result = repo.legacy.k_assistant.db_session.execute(
                                text("SELECT COUNT(*) FROM facts")
                            ).scalar()
                            print(f"   - Direct DB query result: {result}")
                        except Exception as e:
                            print(f"   - DB query failed: {e}")
                    else:
                        print("   - db_session NOT found")
                    
                    # Try get_metrics
                    if hasattr(repo.legacy.k_assistant, 'get_metrics'):
                        print("   - get_metrics exists")
                        try:
                            metrics = repo.legacy.k_assistant.get_metrics()
                            print(f"   - Metrics: {metrics}")
                        except Exception as e:
                            print(f"   - get_metrics failed: {e}")
                    else:
                        print("   - get_metrics NOT found")
                else:
                    print("   - k_assistant NOT found")
            else:
                print("   - legacy proxy NOT initialized")
                
            # Try fallback with get_facts
            print("\n   Trying get_facts fallback...")
            try:
                facts = repo.legacy.get_facts(10)
                print(f"   - get_facts returned {len(facts)} facts (limited to 10)")
                
                # Try with higher limit
                facts_all = repo.legacy.get_facts(5000)
                print(f"   - get_facts with limit 5000: {len(facts_all)} facts")
            except Exception as e:
                print(f"   - get_facts failed: {e}")
        else:
            print(f"   🔍 Unexpected count: {count}")
        
        print("\n3. Testing find_all() for comparison...")
        all_facts = repo.find_all(limit=10)
        print(f"   find_all returned {len(all_facts)} facts (limited to 10)")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Make sure you're in the HAK_GAL_HEXAGONAL directory")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_count_directly()
    
    print("\n" + "=" * 60)
    print("💡 NEXT STEPS:")
    print("=" * 60)
    print("1. If count is 0, check the debug output above")
    print("2. Restart the API: python src_hexagonal/hexagonal_api.py")
    print("3. Run the test again: python test_facts_count_fix.py")
