#!/usr/bin/env python3
"""
HAK_GAL MCP Integration - Final Verification
Checks all components before Claude Desktop integration
"""

import os
import json
import asyncio
import httpx
from pathlib import Path
import subprocess
import sys

class MCPVerification:
    """Complete verification of MCP integration"""
    
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        
    def print_header(self, title):
        """Print section header"""
        print("\n" + "=" * 60)
        print(f" {title}")
        print("=" * 60)
        
    def check_mark(self, passed, message):
        """Print check result"""
        if passed:
            print(f"✅ {message}")
            self.checks_passed += 1
        else:
            print(f"❌ {message}")
            self.checks_failed += 1
            
    def check_file_exists(self, path, description):
        """Check if file exists"""
        exists = Path(path).exists()
        self.check_mark(exists, f"{description}: {path}")
        return exists
        
    async def check_api_running(self):
        """Check if HAK_GAL API is running"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://127.0.0.1:5001/health", timeout=5.0)
                if response.status_code == 200:
                    self.check_mark(True, "HAK_GAL API is running on port 5001")
                    return True
        except:
            pass
        
        self.check_mark(False, "HAK_GAL API is NOT running on port 5001")
        print("   → Run: python src_hexagonal\\hexagonal_api_enhanced_clean.py")
        return False
        
    async def check_facts_available(self):
        """Check if facts are available"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://127.0.0.1:5001/api/facts", 
                                          params={"limit": 1}, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    facts = data.get('facts', [])
                    if facts:
                        self.check_mark(True, f"Knowledge base has facts available")
                        return True
        except:
            pass
            
        self.check_mark(False, "No facts available in knowledge base")
        return False
        
    def check_mcp_server_syntax(self):
        """Check MCP server Python syntax"""
        mcp_server_path = "src_hexagonal/infrastructure/mcp/mcp_server.py"
        if not Path(mcp_server_path).exists():
            self.check_mark(False, f"MCP server not found: {mcp_server_path}")
            return False
            
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", mcp_server_path],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.check_mark(True, "MCP server syntax is valid")
                return True
            else:
                self.check_mark(False, f"MCP server has syntax errors: {result.stderr}")
                return False
        except Exception as e:
            self.check_mark(False, f"Could not check MCP server: {e}")
            return False
            
    def check_claude_config(self):
        """Check Claude Desktop configuration"""
        config_locations = [
            Path(os.environ.get('APPDATA', '')) / 'Claude' / 'claude_desktop_config.json',
            Path.home() / '.config' / 'Claude' / 'claude_desktop_config.json'
        ]
        
        for config_path in config_locations:
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        
                    if 'mcpServers' in config and 'hak-gal' in config['mcpServers']:
                        self.check_mark(True, f"Claude config found and configured: {config_path}")
                        
                        # Check if path is correct
                        mcp_args = config['mcpServers']['hak-gal'].get('args', [])
                        if mcp_args and 'mcp_server.py' in mcp_args[0]:
                            self.check_mark(True, "MCP server path looks correct in config")
                        else:
                            self.check_mark(False, "MCP server path might be wrong in config")
                        return True
                    else:
                        self.check_mark(False, f"Claude config exists but HAK_GAL not configured: {config_path}")
                        print("   → Run: .\\install_claude_config.bat")
                        return False
                except Exception as e:
                    self.check_mark(False, f"Error reading Claude config: {e}")
                    return False
                    
        self.check_mark(False, "Claude Desktop config not found")
        print("   → Run: .\\install_claude_config.bat")
        return False
        
    def check_dependencies(self):
        """Check required Python packages"""
        required = ['httpx', 'flask', 'flask-socketio']
        missing = []
        
        for package in required:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing.append(package)
                
        if not missing:
            self.check_mark(True, "All required packages installed")
            return True
        else:
            self.check_mark(False, f"Missing packages: {', '.join(missing)}")
            print(f"   → Run: pip install {' '.join(missing)}")
            return False
            
    async def run_verification(self):
        """Run all verification checks"""
        self.print_header("HAK_GAL MCP Integration Verification")
        
        # 1. Check files
        print("\n1. Checking files...")
        self.check_file_exists("src_hexagonal/infrastructure/mcp/mcp_server.py", "MCP Server")
        self.check_file_exists("data/k_assistant.db", "Knowledge Base")
        self.check_file_exists("claude_desktop_config_windows.json", "Config template")
        
        # 2. Check dependencies
        print("\n2. Checking dependencies...")
        self.check_dependencies()
        
        # 3. Check HAK_GAL API
        print("\n3. Checking HAK_GAL API...")
        api_running = await self.check_api_running()
        if api_running:
            await self.check_facts_available()
        
        # 4. Check MCP Server
        print("\n4. Checking MCP Server...")
        self.check_mcp_server_syntax()
        
        # 5. Check Claude config
        print("\n5. Checking Claude Desktop configuration...")
        self.check_claude_config()
        
        # Summary
        self.print_header("Verification Summary")
        print(f"✅ Passed: {self.checks_passed}")
        print(f"❌ Failed: {self.checks_failed}")
        
        if self.checks_failed == 0:
            print("\n🎉 All checks passed! Your MCP integration is ready!")
            print("\nNext steps:")
            print("1. Make sure HAK_GAL API is running")
            print("2. Restart Claude Desktop completely")
            print("3. Test by asking Claude about available tools")
        else:
            print("\n⚠️ Some checks failed. Please fix the issues above.")
            print("\nQuick fixes:")
            print("1. Start HAK_GAL API: python src_hexagonal\\hexagonal_api_enhanced_clean.py")
            print("2. Install config: .\\install_claude_config.bat")
            print("3. Install missing packages: pip install httpx")
            
        return self.checks_failed == 0


async def main():
    """Main verification"""
    verifier = MCPVerification()
    success = await verifier.run_verification()
    
    if success:
        print("\n" + "🚀" * 30)
        print("YOUR MCP INTEGRATION IS READY TO USE!")
        print("🚀" * 30)
    
    return success


if __name__ == "__main__":
    print("HAK_GAL MCP Integration - Final Verification")
    print("This will check all components of your MCP setup\n")
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
