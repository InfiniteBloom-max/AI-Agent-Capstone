import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.orchestrator.orchestrator import FlowMindOrchestrator

async def single_question_test():
    """Test orchestrator with a single question"""
    
    print("=" * 80)
    print("FLOWMIND ORCHESTRATOR TEST (Gemma 3)")
    print("=" * 80)
    
    orchestrator = FlowMindOrchestrator()
    question = "What is a Multi-Agent System?"
    
    print(f"\nQuestion: {question}\n")
    
    try:
        result = await orchestrator.ask_tutor(question)
        
        if result.success:
            print("✓ SUCCESS\n")
            print(f"📚 Context Used: {', '.join(result.payload.get('context_used', []))}\n")
            print("🎓 Response:")
            print("-" * 80)
            print(result.payload.get('response', ''))
            print("-" * 80)
            
            if 'critique' in result.payload:
                print(f"\n🔍 Critic: {result.payload['critique']}")
                if 'warning' in result.payload:
                    print(f"⚠️  {result.payload['warning']}")
        else:
            print(f"✗ FAILED: {result.payload.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"✗ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(single_question_test())
