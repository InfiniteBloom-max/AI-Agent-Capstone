import asyncio
import httpx

async def test_multimodal_ingestion():
    """Test the full multimodal ingestion pipeline"""
    
    base_url = "http://127.0.0.1:8000"
    pdf_path = r"C:\Users\Ronit\Downloads\AI Agent Project\Project Writeup.pdf"
    
    print("=" * 80)
    print("TESTING MULTIMODAL INGESTION PIPELINE")
    print("=" * 80)
    
    async with httpx.AsyncClient() as client:
        print(f"\nIngesting: {pdf_path}")
        print("\nThis will:")
        print("  1. Extract text blocks")
        print("  2. Extract concepts from text")
        print("  3. Extract images from PDF")
        print("  4. Process images with vision models")
        print("  5. Combine text + visual concepts")
        print("  6. Map relationships")
        print("\n" + "-" * 80)
        
        try:
            r = await client.post(
                f"{base_url}/ingest",
                json={"pdf_path": pdf_path},
                timeout=300  # 5 minutes
            )
            
            print(f"\nStatus: {r.status_code}")
            
            if r.status_code == 200:
                data = r.json()
                print("\n✓ SUCCESS!\n")
                print(f"📊 Results:")
                print(f"  Total Concepts: {data.get('concepts_count', 0)}")
                print(f"  - Text Concepts: {data.get('text_concepts', 0)}")
                print(f"  - Visual Concepts: {data.get('visual_concepts', 0)}")
                print(f"  Relationships: {data.get('relations_count', 0)}")
            else:
                print(f"\n✗ Error: {r.text}")
        
        except Exception as e:
            print(f"\n✗ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_multimodal_ingestion())
