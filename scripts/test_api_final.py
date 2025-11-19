import asyncio
import httpx

async def test_api():
    """Test the orchestrator API endpoints"""
    
    base_url = "http://localhost:8000"
    
    print("=" * 80)
    print("TESTING FLOWMIND API")
    print("=" * 80)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Health endpoint
        print("\n1. Testing /health endpoint...")
        try:
            r = await client.get(f"{base_url}/health", timeout=10)
            print(f"   Status: {r.status_code}")
            if r.status_code == 200:
                print(f"   ✓ Response: {r.json()}")
            else:
                print(f"   ✗ Error: {r.text}")
        except Exception as e:
            print(f"   ✗ Exception: {e}")
        
        await asyncio.sleep(2)
        
        # Test 2: Ask endpoint
        print("\n2. Testing /ask endpoint...")
        try:
            r = await client.post(
                f"{base_url}/ask",
                json={"query": "What is a Multi-Agent System?"},
                timeout=60
            )
            print(f"   Status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(f"   ✓ Context: {data.get('context_used', [])}")
                response_text = data.get('response', '')
                print(f"   ✓ Response preview: {response_text[:200]}...")
            else:
                print(f"   ✗ Error: {r.text}")
        except Exception as e:
            print(f"   ✗ Exception: {e}")
    
    print("\n" + "=" * 80)
    print("API TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    print("\n⏳ Waiting for server to start...\n")
    asyncio.run(asyncio.sleep(5))  # Give server time to start
    asyncio.run(test_api())
