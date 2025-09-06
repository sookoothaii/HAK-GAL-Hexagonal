#!/usr/bin/env python3
"""
HAK-GAL API Endpoint Discovery
===============================
Findet die richtigen API-Endpoints
"""

import requests
import json

def discover_endpoints():
    """
    Testet verschiedene Ports und Endpoints
    """
    print("🔍 DISCOVERING HAK-GAL API ENDPOINTS")
    print("="*60)
    
    # Mögliche Ports
    ports = [5000, 5001, 5002, 5173, 8000, 8080, 3000]
    
    # Mögliche Endpoints
    endpoints = [
        '/api/status',
        '/api/health',
        '/api/system/stats',
        '/api/knowledge-base/status',
        '/api/command',
        '/api/reason',
        '/api/facts',
        '/api/llm/query',
        '/api/llm/analyze',
        '/api/llm/get-explanation',
        '/api/query',
        '/api/analyze',
        '/health',
        '/status'
    ]
    
    working_endpoints = []
    
    for port in ports:
        print(f"\n🔍 Testing port {port}...")
        base_url = f"http://localhost:{port}"
        
        # Test base connection
        try:
            response = requests.get(f"{base_url}/", timeout=1)
            print(f"  ✅ Port {port} is responsive!")
            
            # Test endpoints
            for endpoint in endpoints:
                try:
                    # Try GET first
                    response = requests.get(f"{base_url}{endpoint}", timeout=1)
                    if response.status_code != 404:
                        print(f"    ✅ GET {endpoint}: {response.status_code}")
                        working_endpoints.append({
                            'port': port,
                            'endpoint': endpoint,
                            'method': 'GET',
                            'status': response.status_code
                        })
                except:
                    pass
                
                try:
                    # Try POST
                    response = requests.post(
                        f"{base_url}{endpoint}", 
                        json={'test': 'test'},
                        headers={'Content-Type': 'application/json'},
                        timeout=1
                    )
                    if response.status_code not in [404, 405]:
                        print(f"    ✅ POST {endpoint}: {response.status_code}")
                        working_endpoints.append({
                            'port': port,
                            'endpoint': endpoint,
                            'method': 'POST',
                            'status': response.status_code
                        })
                except:
                    pass
                    
        except Exception as e:
            print(f"  ❌ Port {port} not accessible")
    
    # Summary
    print("\n" + "="*60)
    print("📊 WORKING ENDPOINTS FOUND:")
    print("="*60)
    
    if working_endpoints:
        current_port = None
        for ep in working_endpoints:
            if ep['port'] != current_port:
                current_port = ep['port']
                print(f"\n🔌 Port {current_port}:")
            print(f"  • {ep['method']:4} {ep['endpoint']} → {ep['status']}")
    else:
        print("❌ No working endpoints found!")
        print("\n💡 Make sure the backend is running:")
        print("  cd D:\\MCP Mods\\HAK_GAL_HEXAGONAL")
        print("  python src/hak_gal/api.py")
    
    return working_endpoints

def test_llm_endpoints(port=5000):
    """
    Testet spezifische LLM-Endpoints
    """
    print(f"\n🤖 TESTING LLM ENDPOINTS ON PORT {port}")
    print("="*60)
    
    base_url = f"http://localhost:{port}"
    
    # Mögliche LLM-Endpoints basierend auf HAK-GAL Struktur
    llm_endpoints = [
        # Standard API-Style
        ('/api/command', {'command': 'ask', 'query': 'What is AI?'}),
        ('/api/reason', {'query': 'IsA(Socrates, Philosopher)'}),
        ('/api/analyze', {'fact': 'IsA(Socrates, Philosopher)'}),
        
        # LLM-specific
        ('/api/llm/query', {'query': 'Test query'}),
        ('/api/llm/analyze', {'query': 'Test'}),
        ('/api/llm/get-explanation', {'topic': 'AI', 'context_facts': []}),
        
        # Alternative patterns
        ('/llm/query', {'query': 'Test'}),
        ('/query', {'q': 'Test'}),
        ('/analyze', {'text': 'Test'}),
    ]
    
    for endpoint, payload in llm_endpoints:
        try:
            response = requests.post(
                f"{base_url}{endpoint}",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ {endpoint} WORKS!")
                print(f"   Payload: {payload}")
                
                # Show response preview
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        preview = str(data)[:100]
                        print(f"   Response: {preview}...")
                except:
                    pass
                    
            elif response.status_code == 405:
                print(f"❌ {endpoint}: Method not allowed")
            elif response.status_code == 404:
                print(f"❌ {endpoint}: Not found")
            else:
                print(f"⚠️ {endpoint}: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint}: {str(e)[:50]}")
    
    print("\n💡 TIP: If no LLM endpoints work, the backend might not have LLM configured")

def find_correct_api():
    """
    Hauptfunktion zum Finden der richtigen API
    """
    print("\n🚀 HAK-GAL API ENDPOINT DISCOVERY")
    print("="*60)
    
    # 1. Discover all endpoints
    working = discover_endpoints()
    
    # 2. Find most likely port
    if working:
        ports = set(ep['port'] for ep in working)
        most_likely_port = max(ports, key=lambda p: sum(1 for ep in working if ep['port'] == p))
        
        print(f"\n🎯 Most likely port: {most_likely_port}")
        
        # 3. Test LLM endpoints on that port
        test_llm_endpoints(most_likely_port)
    else:
        # Try default port anyway
        print("\n🔧 Trying default port 5000...")
        test_llm_endpoints(5000)
    
    print("\n" + "="*60)
    print("📝 RECOMMENDATIONS:")
    print("="*60)
    print("1. Use the working endpoints found above")
    print("2. The LLM might be at /api/command with 'ask' command")
    print("3. Or use /api/reason for HRM reasoning")
    print("4. Check if LLM services are configured in backend")

if __name__ == "__main__":
    find_correct_api()
