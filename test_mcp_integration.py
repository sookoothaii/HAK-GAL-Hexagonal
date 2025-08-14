#!/usr/bin/env python3
"""
Test-Skript für HAK_GAL MCP Server
Testet die Integration ohne Claude Desktop
"""

import asyncio
import httpx
import json
from typing import Dict

async def test_mcp_tools():
    """Test MCP tools by calling HAK_GAL API directly"""
    
    api_url = "http://127.0.0.1:5001"
    
    print("=" * 60)
    print("HAK_GAL MCP Integration Test")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: System Status
        print("\n1. Testing System Status...")
        try:
            response = await client.get(f"{api_url}/api/status", params={"light": "1"})
            if response.status_code == 200:
                data = response.json()
                print(f"✅ System Status: {data.get('architecture', 'unknown')}")
                print(f"   Facts loaded: {data.get('kb_facts_count', 0)}")
                print(f"   LLM providers: {data.get('llm_providers', [])}")
                
                # Warnung wenn keine Facts geladen
                if data.get('kb_facts_count', 0) == 0:
                    print("   ⚠️  WARNING: No facts loaded in knowledge base!")
                    print("   Check if legacy adapters are working correctly")
            else:
                print(f"❌ Status check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Connection error: {e}")
            print("   Is HAK_GAL running on port 5001?")
            return
        
        # Test 2: Search Knowledge
        print("\n2. Testing Knowledge Search...")
        try:
            response = await client.post(
                f"{api_url}/api/search",
                json={"query": "hexagonal", "limit": 3}
            )
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                print(f"✅ Found {len(results)} facts")
                for fact in results[:3]:
                    # Handle fact as string or dict
                    if isinstance(fact, str):
                        print(f"   - {fact[:80]}..." if len(fact) > 80 else f"   - {fact}")
                    elif isinstance(fact, dict):
                        fact_str = str(fact.get('statement', fact))
                        print(f"   - {fact_str[:80]}..." if len(fact_str) > 80 else f"   - {fact_str}")
                    else:
                        print(f"   - {str(fact)[:80]}...")
            else:
                print(f"❌ Search failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Search error: {e}")
        
        # Test 3: Neural Reasoning
        print("\n3. Testing Neural Reasoning...")
        try:
            response = await client.post(
                f"{api_url}/api/reason",
                json={"query": "What is hexagonal architecture?"}
            )
            if response.status_code == 200:
                data = response.json()
                confidence = data.get('confidence', 0)
                result = data.get('result', 'No result')
                
                print(f"✅ Reasoning confidence: {confidence:.4f}")
                if isinstance(result, str):
                    print(f"   Result: {result[:100]}..." if len(result) > 100 else f"   Result: {result}")
                else:
                    print(f"   Result: {str(result)[:100]}...")
                    
                if confidence == 0:
                    print("   ⚠️  WARNING: Confidence is 0, HRM might not be initialized")
            else:
                print(f"❌ Reasoning failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Reasoning error: {e}")
        
        # Test 4: List Facts
        print("\n4. Testing List Facts...")
        try:
            response = await client.get(
                f"{api_url}/api/facts",
                params={"limit": 5}
            )
            if response.status_code == 200:
                data = response.json()
                facts = data.get('facts', [])
                print(f"✅ Retrieved {len(facts)} facts")
                
                # Show first 3 facts
                for i, fact in enumerate(facts[:3], 1):
                    # Handle different fact formats
                    if isinstance(fact, str):
                        fact_str = fact
                    elif isinstance(fact, dict):
                        fact_str = fact.get('statement', str(fact))
                    else:
                        fact_str = str(fact)
                    
                    # Truncate if too long
                    if len(fact_str) > 80:
                        print(f"   {i}. {fact_str[:80]}...")
                    else:
                        print(f"   {i}. {fact_str}")
            else:
                print(f"❌ List facts failed: {response.status_code}")
        except Exception as e:
            print(f"❌ List facts error: {e}")
        
        # Test 5: Check facts count
        print("\n5. Testing Facts Count...")
        try:
            response = await client.get(f"{api_url}/api/facts/count")
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                total = data.get('total', 0)
                print(f"✅ Facts count: {count}, Total: {total}")
            else:
                print(f"❌ Facts count failed: {response.status_code}")
        except Exception as e:
            print(f"   Facts count endpoint might not exist: {e}")
    
    print("\n" + "=" * 60)
    print("MCP Integration Test Complete")
    print("\n⚠️  IMPORTANT NOTES:")
    
    # Check for common issues
    print("\nIf you see 0 facts loaded:")
    print("1. Check if k_assistant.db exists in data/ folder")
    print("2. Legacy adapters might need initialization")
    print("3. Try restarting the API")
    
    print("\nTo use with Claude Desktop:")
    print("1. Copy claude_desktop_config.json content to:")
    print("   Windows: %APPDATA%\\Claude\\claude_desktop_config.json")
    print("   Linux/Mac: ~/.config/Claude/claude_desktop_config.json")
    print("2. Restart Claude Desktop")
    print("3. HAK_GAL tools will be available in Claude")
    print("=" * 60)


def test_mcp_protocol():
    """Test MCP protocol message formatting"""
    
    print("\n" + "=" * 60)
    print("MCP Protocol Message Examples")
    print("=" * 60)
    
    # Example messages
    messages = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "0.1.0"}
        },
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        },
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "search_knowledge",
                "arguments": {"query": "test", "limit": 5}
            }
        }
    ]
    
    for msg in messages:
        print(f"\n{msg['method']}:")
        print(json.dumps(msg, indent=2))


async def check_api_details():
    """Check API details to understand the issue"""
    
    print("\n" + "=" * 60)
    print("Checking API Details")
    print("=" * 60)
    
    api_url = "http://127.0.0.1:5001"
    
    async with httpx.AsyncClient() as client:
        # Check health
        print("\nChecking /health endpoint...")
        try:
            response = await client.get(f"{api_url}/health")
            print(f"Health status: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"Health check error: {e}")
        
        # Check full status
        print("\nChecking full /api/status endpoint...")
        try:
            response = await client.get(f"{api_url}/api/status")
            if response.status_code == 200:
                data = response.json()
                print(f"Full status response keys: {list(data.keys())}")
                if 'kb_facts_count' in data:
                    print(f"KB facts count: {data['kb_facts_count']}")
                if 'system_state' in data:
                    print(f"System state: {data.get('system_state', {}).get('facts_loaded', 'unknown')}")
        except Exception as e:
            print(f"Full status error: {e}")


if __name__ == "__main__":
    print("Testing HAK_GAL MCP Integration...")
    print("\nMake sure HAK_GAL is running on port 5001!")
    print("Run: python src_hexagonal/hexagonal_api_enhanced_clean.py\n")
    
    # Test API connectivity
    asyncio.run(test_mcp_tools())
    
    # Check API details
    asyncio.run(check_api_details())
    
    # Show protocol examples
    test_mcp_protocol()
