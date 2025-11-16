from ..orchestrator.agent_base import BaseAgent, AgentResult
from ..tools.llm_clients import LLMClient
from ..tools.vector_store import VectorStore
from ..tools.graph_store import GraphStore
from typing import Dict, Any
import json

class ConceptExtractionAgent(BaseAgent):
    name = "concept_agent"

    def __init__(self):
        self.llm = LLMClient()
        # Lazy init stores to avoid connection issues during import if env vars aren't set
        self.vector_store = None 
        self.graph_store = None

    async def run(self, context: Dict[str, Any]) -> AgentResult:
        blocks = context.get("blocks")
        if not blocks:
            return AgentResult(success=False, payload={"error": "No blocks provided"})

        if not self.vector_store: self.vector_store = VectorStore()
        if not self.graph_store: self.graph_store = GraphStore()

        # Combine all blocks into one text (limit to first 50 blocks to avoid context limits)
        max_blocks = min(50, len(blocks))
        text_content = "\n\n".join([b['content'] for b in blocks[:max_blocks]])
        
        # Truncate if too long (rough estimate: keep under 6000 words)
        words = text_content.split()
        if len(words) > 6000:
            text_content = " ".join(words[:6000]) + "..."
        
        prompt = f"""
        Analyze the following document and extract ONLY the top 10 most important concepts.
        Return a JSON list with exactly 10 objects, each with keys: 'name', 'definition', 'importance' (1-10).
        Focus on the core concepts that are most central to understanding this document.
        
        Text:
        {text_content}
        
        Return format:
        [
          {{"name": "Concept Name", "definition": "Clear definition", "importance": 10}},
          ...
        ]
        """
        
        extracted_concepts = []
        
        try:
            print("Extracting top 10 concepts from document...")
            response = await self.llm.generate(
                messages=[{"role": "user", "content": prompt}],
                provider="mistral",
                model="mistral-large-latest",
                temperature=0.3
            )
            
            # Parse LLM response
            clean_response = response.replace("```json", "").replace("```", "").strip()
            
            # Handle case where LLM adds text before/after JSON
            if "[" in clean_response and "]" in clean_response:
                start = clean_response.find("[")
                end = clean_response.rfind("]") + 1
                clean_response = clean_response[start:end]
            
            concepts = json.loads(clean_response)
            
            # Limit to top 10 by importance
            concepts = sorted(concepts, key=lambda x: x.get('importance', 0), reverse=True)[:10]
            
            print(f"Successfully extracted {len(concepts)} concepts")
            
            for idx, concept in enumerate(concepts):
                # Generate real embedding
                embedding_text = f"{concept['name']}: {concept['definition']}"
                print(f"  Generating embedding for: {concept['name']}")
                embedding = await self.llm.embed(embedding_text)
                
                concept_id = f"concept_{idx}"
                
                # Store in Vector DB
                self.vector_store.upsert([(concept_id, embedding, concept)])
                
                # Store in Graph DB
                self.graph_store.add_concept(
                    concept['name'], 
                    concept['definition'], 
                    concept_id, 
                    {"doc_id": "doc_1", "page": 1}
                )
                
                extracted_concepts.append(concept)
                print(f"  - {concept['name']} (importance: {concept.get('importance', 'N/A')})")
                
        except Exception as e:
            print(f"Error extracting concepts: {e}")
            if 'response' in locals():
                print(f"Raw response: {response[:500]}...")

        return AgentResult(success=True, payload={"concepts": extracted_concepts})
