import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.ingestion.vision_agent import VisionConceptAgent

async def test_vision():
    """Test vision-based concept extraction"""
    
    pdf_path = r"C:\Users\Ronit\Downloads\AI Agent Project\Project Writeup.pdf"
    
    print("=" * 80)
    print("TESTING VISION CONCEPT EXTRACTION")
    print("=" * 80)
    
    agent = VisionConceptAgent()
    
    try:
        result = await agent.run({"pdf_path": pdf_path})
        
        if result.success:
            visual_concepts = result.payload.get('visual_concepts', [])
            
            print(f"\n✓ Successfully extracted {len(visual_concepts)} visual concepts\n")
            
            for i, concept in enumerate(visual_concepts, 1):
                print(f"\n{'-' * 80}")
                print(f"Visual Concept {i}:")
                print(f"{'-' * 80}")
                print(f"Page: {concept.get('page')}")
                print(f"Type: {concept.get('type')}")
                print(f"Description: {concept.get('description')}")
                print(f"Related Concepts: {', '.join(concept.get('concepts', []))}")
                print(f"Relevance: {concept.get('relevance')}")
        else:
            print(f"✗ Failed: {result.payload}")
    
    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_vision())
