import asyncio
import httpx

async def test_feedback():
    """Test the feedback endpoint"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("=" * 80)
    print("TESTING FEEDBACK LOOP")
    print("=" * 80)
    
    feedback_data = {
        "query": "What is a Multi-Agent System?",
        "response": "A system with multiple agents...",
        "rating": 5,
        "comments": "Great explanation!",
        "improved_response": None
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print("\nSubmitting feedback...")
            r = await client.post(
                f"{base_url}/feedback",
                json=feedback_data,
                timeout=10
            )
            
            print(f"Status: {r.status_code}")
            if r.status_code == 200:
                print(f"✓ Response: {r.json()}")
            else:
                print(f"✗ Error: {r.text}")
                
        except Exception as e:
            print(f"✗ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_feedback())
