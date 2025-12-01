import asyncio
import sys
import os

# Script to test ingetsion by adding a sample document 
# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.orchestrator.orchestrator import FlowMindOrchestrator

async def main():
    if len(sys.argv) < 2:
        print("Usage: python ingest_sample.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    orchestrator = FlowMindOrchestrator()
    
    print(f"Ingesting {pdf_path}...")
    result = await orchestrator.ingest_pdf(pdf_path)
    
    if result.success:
        print("Ingestion successful!")
        print(result.payload)
    else:
        print("Ingestion failed.")
        print(result.payload)

if __name__ == "__main__":
    asyncio.run(main())
