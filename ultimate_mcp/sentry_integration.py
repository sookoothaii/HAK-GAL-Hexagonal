# D:\MCP Mods\HAK_GAL_HEXAGONAL\ultimate_mcp\sentry_integration.py
"""
Sentry monitoring integration for HAK_GAL system
Created: 2025-01-04
"""
import os
import sys
import requests
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class SentryIntegration:
    """Sentry monitoring integration for HAK_GAL system"""
    
    def __init__(self):
        self.dsn = (os.getenv('SENTRY_DSN') or '').strip().strip('"')
        self.auth_token = os.getenv('SENTRY_AUTH_TOKEN')
        self.org = os.getenv('SENTRY_ORG', 'samui-science-lab')
        self.region_url = os.getenv('SENTRY_REGION_URL', 'https://de.sentry.io')
        self.project_id = os.getenv('SENTRY_PROJECT_ID', '4509659832189008')
        self.sdk_initialized = False
        
        # Optional: Initialize Sentry SDK only if DSN is valid
        if self.dsn and self.dsn.startswith('https://'):
            try:
                import sentry_sdk
                sentry_sdk.init(
                    dsn=self.dsn,
                    traces_sample_rate=0.1,
                    environment=os.getenv('SENTRY_ENVIRONMENT', 'hakgal_production')
                )
                self.sdk_initialized = True
                logger.info("Sentry SDK initialized successfully")
            except Exception as e:
                logger.warning(f"Sentry SDK initialization failed: {e}")
                self.sdk_initialized = False
        else:
            logger.info("Sentry SDK not initialized - DSN not configured or invalid")
    
    def whoami(self) -> Dict[str, Any]:
        """Get authenticated user info"""
        if not self.auth_token:
            return {"error": "SENTRY_AUTH_TOKEN not configured"}
        
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        response = requests.get(f'{self.region_url}/api/0/', headers=headers)
        
        if response.ok:
            data = response.json()
            return {
                "user": data.get("user", {}),
                "auth": data.get("auth", {})
            }
        return {"error": f"API error: {response.status_code}"}
    
    def find_organizations(self) -> List[Dict[str, Any]]:
        """List accessible organizations"""
        if not self.auth_token:
            return [{"error": "SENTRY_AUTH_TOKEN not configured"}]
        
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        response = requests.get(
            f'{self.region_url}/api/0/organizations/',
            headers=headers
        )
        
        if response.ok:
            return response.json()
        return [{"error": f"API error: {response.status_code}"}]
    
    def find_projects(self, organization_slug: str = None) -> List[Dict[str, Any]]:
        """List projects in organization"""
        if not self.auth_token:
            return [{"error": "SENTRY_AUTH_TOKEN not configured"}]
        
        org = organization_slug or self.org
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        response = requests.get(
            f'{self.region_url}/api/0/organizations/{org}/projects/',
            headers=headers
        )
        
        if response.ok:
            return response.json()
        return [{"error": f"API error: {response.status_code}"}]
    
    def search_issues(self, query: str = "", limit: int = 10) -> Dict[str, Any]:
        """Search for issues"""
        if not self.auth_token:
            return {"error": "SENTRY_AUTH_TOKEN not configured"}
        
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        params = {
            'query': query or 'is:unresolved',
            'limit': limit,
            'project': self.project_id
        }
        
        response = requests.get(
            f'{self.region_url}/api/0/organizations/{self.org}/issues/',
            headers=headers,
            params=params
        )
        
        if response.ok:
            return {"issues": response.json()}
        return {"error": f"API error: {response.status_code}"}
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Sentry connection and configuration"""
        result = {
            "dsn_configured": bool(self.dsn),
            "dsn_valid": bool(self.dsn and self.dsn.startswith('https://')),
            "sdk_initialized": self.sdk_initialized,
            "auth_token_configured": bool(self.auth_token),
            "organization": self.org,
            "region": self.region_url,
            "project_id": self.project_id
        }
        
        if self.auth_token:
            orgs = self.find_organizations()
            if not isinstance(orgs, list) or (orgs and "error" in orgs[0]):
                result["api_status"] = "failed"
                result["api_error"] = orgs
            else:
                result["api_status"] = "connected"
                result["organizations_found"] = len(orgs)
        else:
            result["api_status"] = "no_auth_token"
        
        return result

if __name__ == "__main__":
    # Test when run directly
    from dotenv import load_dotenv
    load_dotenv()
    
    sentry = SentryIntegration()
    print("Testing Sentry Integration...")
    result = sentry.test_connection()
    print(f"Connection Test: {result}")
    
    if result.get("api_status") == "connected":
        print("\nOrganizations:")
        orgs = sentry.find_organizations()
        for org in orgs:
            print(f"  - {org.get('slug')}: {org.get('name')}")
