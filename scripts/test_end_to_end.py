import asyncio
import httpx
import os

async def test_full_flow():
    """
    End-to-end test:
    1. Upload PDF via /ingest
    2. Ask 4 questions via /ask
    """
    
    base_url = "http://127.0.0.1:8000"
    pdf_path = r"C:\Users\Ronit\Downloads\AI Agent Project\Project Writeup.pdf"
    
    print("=" * 80)
    print("FLOWMIND END-TO-END TEST")
    print("=" * 80)
    
    # Verify PDF exists
    if not os.path.exists(pdf_path):
        print(f"\n✗ PDF not found: {pdf_path}")
        return
    
    print(f"\n📄 PDF: {os.path.basename(pdf_path)}")
    
    async with httpx.AsyncClient() as client:
        # STEP 1: Ingest PDF
        print("\n" + "=" * 80)
        print("STEP 1: INGESTING PDF")
        print("=" * 80)
        
        try:
            print(f"\nUploading to /ingest endpoint...")
            r = await client.post(
                f"{base_url}/ingest",
                json={"pdf_path": pdf_path},
                timeout=300  # 5 minutes for ingestion
            )
            
            print(f"Status: {r.status_code}")
            
            if r.status_code == 200:
                data = r.json()
                print(f"✓ Ingestion successful!")
                print(f"  - Concepts extracted: {data.get('concepts_count', 0)}")
                print(f"  - Relations mapped: {data.get('relations_count', 0)}")
            else:
                print(f"✗ Ingestion failed: {r.text}")
                return
        
        except Exception as e:
            print(f"✗ Exception during ingestion: {e}")
            return
        
        # Wait a bit for data to settle
        print("\n⏳ Waiting 5 seconds for data to settle...")
        await asyncio.sleep(5)
        
        # STEP 2: Ask Questions
        print("\n" + "=" * 80)
        print("STEP 2: ASKING QUESTIONS")
        print("=" * 80)
        
        questions = [
            "What is a Multi-Agent System?",
            "Explain the Pedagogy Swarm.",
            "How does FlowMind prevent hallucinations?",
            "What is the role of the Concept Graph?"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n{'-' * 80}")
            print(f"QUESTION {i}/{len(questions)}")
            print(f"{'-' * 80}")
            print(f"❓ {question}\n")
            
            try:
                r = await client.post(
                    f"{base_url}/ask",
                    json={"query": question},
                    timeout=60
                )
                
                if r.status_code == 200:
                    data = r.json()
                    print(f"📚 Context: {', '.join(data.get('context_used', []))}\n")
                    print(f"🎓 Answer:")
                    print(data.get('response', ''))
                    
                    if 'warning' in data:
                        print(f"\n⚠️  {data['warning']}")
                else:
                    print(f"✗ Error: {r.text}")
            
            except Exception as e:
                print(f"✗ Exception: {e}")
            
            # Wait between questions to avoid rate limits
            if i < len(questions):
                print(f"\n⏳ Waiting 8 seconds before next question...")
                await asyncio.sleep(8)
        
        print("\n" + "=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_full_flow())
