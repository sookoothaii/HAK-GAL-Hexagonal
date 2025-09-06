#!/usr/bin/env python3
"""
Test-Skript fuer Sentry Integration
Created: 2025-01-04
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"[OK] Loaded .env from {env_path}")
else:
    print("[WARNING] No .env file found")

# Test Sentry Integration
try:
    from sentry_integration import SentryIntegration
    print("[OK] Sentry integration module loaded")
    
    # Create instance
    sentry = SentryIntegration()
    print(f"[OK] Sentry instance created")
    print(f"    Organization: {sentry.org}")
    print(f"    Region: {sentry.region_url}")
    print(f"    Project ID: {sentry.project_id}")
    
    # Test connection
    print("\n[TEST] Connection Test...")
    result = sentry.test_connection()
    print(f"    DSN Configured: {result.get('dsn_configured')}")
    print(f"    Auth Token: {result.get('auth_token_configured')}")
    print(f"    API Status: {result.get('api_status')}")
    
    if result.get('api_status') == 'connected':
        print(f"    ✓ Successfully connected!")
        print(f"    Organizations Found: {result.get('organizations_found')}")
        
        # List organizations
        print("\n[TEST] Find Organizations...")
        orgs = sentry.find_organizations()
        if not isinstance(orgs, list) or (orgs and "error" in orgs[0]):
            print(f"    ✗ Error: {orgs}")
        else:
            for org in orgs:
                print(f"    - {org.get('slug')}: {org.get('name')}")
        
        # List projects
        print("\n[TEST] Find Projects...")
        projects = sentry.find_projects()
        if isinstance(projects, list) and not (projects and "error" in projects[0]):
            print(f"    Found {len(projects)} project(s)")
            for proj in projects[:3]:
                print(f"    - {proj.get('slug')}: {proj.get('name')} ({proj.get('platform')})")
        
        # Search issues
        print("\n[TEST] Search Issues...")
        issues_result = sentry.search_issues("", 3)
        if "error" not in issues_result:
            issues = issues_result.get("issues", [])
            print(f"    Found {len(issues)} issue(s)")
            for issue in issues[:3]:
                print(f"    - {issue.get('shortId')}: {issue.get('title')[:50]}...")
    else:
        print(f"    ✗ Connection failed: {result.get('api_status')}")
        if result.get('api_error'):
            print(f"    Error: {result.get('api_error')}")
            
    print("\n[SUCCESS] Sentry integration test complete!")
    
except ImportError as e:
    print(f"[ERROR] Failed to import sentry_integration: {e}")
    print("Make sure to install: pip install sentry-sdk requests")
except Exception as e:
    print(f"[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
