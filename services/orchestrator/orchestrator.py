from .agent_base import AgentResult
from ..ingestion.parsing_agent import ParsingAgent
from ..ingestion.concept_agent import ConceptExtractionAgent
from ..ingestion.vision_agent import VisionConceptAgent
from ..ingestion.relation_agent import RelationshipMappingAgent
from ..pedagogy.teaching_agent import TeachingAgent
from ..pedagogy.critic_agent import CriticAgent
import logging

logger = logging.getLogger(__name__)

class FlowMindOrchestrator:
    def __init__(self):
        self.parsing_agent = ParsingAgent()
        self.concept_agent = ConceptExtractionAgent()
        self.vision_agent = VisionConceptAgent()
        self.relation_agent = RelationshipMappingAgent()
        self.teaching_agent = TeachingAgent()
        self.critic_agent = CriticAgent()

    async def ingest_pdf(self, pdf_path: str):
        logger.info(f"Starting multimodal ingestion for {pdf_path}")
        
        # 1. Parse text
        parse_result = await self.parsing_agent.run({"pdf_path": pdf_path})
        if not parse_result.success:
            return parse_result
            
        blocks = parse_result.payload["blocks"]
        
        # 2. Extract text concepts
        concept_result = await self.concept_agent.run({"blocks": blocks})
        if not concept_result.success:
            return concept_result
            
        text_concepts = concept_result.payload["concepts"]
        logger.info(f"Extracted {len(text_concepts)} text concepts")
        
        # 3. Extract visual concepts from images
        vision_result = await self.vision_agent.run({"pdf_path": pdf_path})
        visual_concepts = []
        
        if vision_result.success:
            visual_data = vision_result.payload.get("visual_concepts", [])
            
            # Convert visual concepts to standard concept format
            for vc in visual_data:
                visual_concept = {
                    "name": f"Visual: {vc.get('type', 'Image')} (Page {vc.get('page')})",
                    "definition": vc.get('description', ''),
                    "importance": 8,  # Visual concepts are important
                    "type": "visual",
                    "page": vc.get('page'),
                    "related_concepts": vc.get('concepts', [])
                }
                visual_concepts.append(visual_concept)
            
            logger.info(f"Extracted {len(visual_concepts)} visual concepts")
        else:
            logger.warning("Visual concept extraction failed, continuing with text only")
        
        # 4. Combine text and visual concepts
        all_concepts = text_concepts + visual_concepts
        logger.info(f"Total concepts: {len(all_concepts)} ({len(text_concepts)} text + {len(visual_concepts)} visual)")
        
        # 5. Map Relationships
        relation_result = await self.relation_agent.run({"concepts": all_concepts})
        
        return AgentResult(
            success=True, 
            payload={
                "concepts_count": len(all_concepts),
                "text_concepts": len(text_concepts),
                "visual_concepts": len(visual_concepts),
                "relations_count": len(relation_result.payload.get("relations", []))
            }
        )


    async def ask_tutor(self, query: str):
        # 1. Get initial answer
        teach_result = await self.teaching_agent.run({"query": query})
        if not teach_result.success:
            return teach_result
            
        response = teach_result.payload["response"]
        context_used = teach_result.payload["context_used"]
        
        # 2. Critique
        critic_result = await self.critic_agent.run({
            "proposed_response": response,
            "source_context": str(context_used)
        })
        
        if critic_result.payload.get("approved"):
            return teach_result
        else:
            # Simple retry logic or return with warning
            # For now, just append the critique
            return AgentResult(
                success=True, 
                payload={
                    "response": response,
                    "critique": critic_result.payload["critique"],
                    "warning": "Response may need improvement."
                }
            )
