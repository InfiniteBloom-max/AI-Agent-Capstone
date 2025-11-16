from ..orchestrator.agent_base import BaseAgent, AgentResult
from ..tools.llm_clients import LLMClient
from ..tools.graph_store import GraphStore
from typing import Dict, Any
import json

class RelationshipMappingAgent(BaseAgent):
    name = "relation_agent"

    def __init__(self):
        self.llm = LLMClient()
        self.graph_store = None

    async def run(self, context: Dict[str, Any]) -> AgentResult:
        concepts = context.get("concepts")
        if not concepts:
            return AgentResult(success=False, payload={"error": "No concepts provided"})

        if not self.graph_store: self.graph_store = GraphStore()

        # Limit to top 10 concepts to avoid overwhelming the LLM
        concepts = concepts[:10]
        concept_names = [c['name'] for c in concepts]
        
        print(f"Mapping relationships between {len(concept_names)} concepts...")
        
        prompt = f"""
        Identify the most important relationships between these concepts: {', '.join(concept_names)}.
        Return a JSON list of relationship objects with keys: 'source', 'target', 'relation_type', 'confidence'.
        Relation types: Prerequisite, IsA, PartOf, RelatedTo, Uses, Extends.
        Only include relationships where confidence > 0.7.
        Limit to maximum 15 relationships.
        
        Example format:
        [
          {{"source": "ConceptA", "target": "ConceptB", "relation_type": "Prerequisite", "confidence": 0.9}},
          ...
        ]
        """
        
        try:
            print("Calling LLM for relationship mapping...")
            response = await self.llm.generate(
                messages=[{"role": "user", "content": prompt}],
                provider="mistral",
                model="mistral-large-latest",
                temperature=0.3
            )
            
            clean_response = response.replace("```json", "").replace("```", "").strip()
            
            # Extract JSON array
            if "[" in clean_response and "]" in clean_response:
                start = clean_response.find("[")
                end = clean_response.rfind("]") + 1
                clean_response = clean_response[start:end]
            
            relations = json.loads(clean_response)
            
            print(f"Found {len(relations)} relationships")
            
            for rel in relations:
                if rel['source'] in concept_names and rel['target'] in concept_names:
                    self.graph_store.add_relation(
                        rel['source'], 
                        rel['target'], 
                        rel['relation_type'], 
                        rel['confidence']
                    )
                    print(f"  - {rel['source']} -> {rel['target']} ({rel['relation_type']})")
            
            return AgentResult(success=True, payload={"relations": relations})
            
        except Exception as e:
            print(f"Error mapping relationships: {e}")
            if 'response' in locals():
                print(f"Raw response: {response[:500]}...")
            return AgentResult(success=False, payload={"error": str(e), "relations": []})
