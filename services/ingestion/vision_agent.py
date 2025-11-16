from ..orchestrator.agent_base import BaseAgent, AgentResult
from ..tools.llm_clients import LLMClient
from ..tools.image_extractor import ImageExtractor
import asyncio

class VisionConceptAgent(BaseAgent):
    """Extract concepts from images using vision models"""
    
    def __init__(self):
        self.llm = LLMClient()
        self.image_extractor = ImageExtractor()
    
    async def run(self, context):
        """
        Process images from PDF and extract visual concepts
        
        Args:
            context: {'pdf_path': str}
        
        Returns:
            AgentResult with visual concepts
        """
        pdf_path = context['pdf_path']
        
        # Extract images
        print(f"\nExtracting images from PDF...")
        images = self.image_extractor.extract_images(pdf_path)
        
        if not images:
            print("No images found in PDF")
            return AgentResult(success=True, payload={"visual_concepts": []})
        
        print(f"Found {len(images)} images")
        
        visual_concepts = []
        
        # Process each image (limit to first 5 to avoid rate limits)
        max_images = min(5, len(images))
        
        for i, img_info in enumerate(images[:max_images]):
            print(f"\nProcessing image {i+1}/{max_images} (Page {img_info['page']})...")
            
            try:
                prompt = """Analyze this image and provide:
1. What type of visual is this? (diagram, chart, graph, screenshot, photo, equation, etc.)
2. A detailed description of what it shows
3. Key concepts or information it conveys
4. How it relates to the document's content

Format your response as JSON:
{
  "type": "diagram/chart/graph/etc",
  "description": "detailed description",
  "concepts": ["concept1", "concept2"],
  "relevance": "how it relates to the document"
}
"""
                
                response = await self.llm.process_vision(
                    img_info['path'],
                    prompt
                )
                
                # Parse response
                import json
                clean_response = response.replace("```json", "").replace("```", "").strip()
                
                if "{" in clean_response and "}" in clean_response:
                    start = clean_response.find("{")
                    end = clean_response.rfind("}") + 1
                    clean_response = clean_response[start:end]
                
                visual_data = json.loads(clean_response)
                visual_data['page'] = img_info['page']
                visual_data['image_path']  = img_info['path']
                
                visual_concepts.append(visual_data)
                print(f"  Type: {visual_data.get('type', 'unknown')}")
                print(f"  Concepts: {', '.join(visual_data.get('concepts', []))}")
                
                # Rate limit delay
                if i < max_images - 1:
                    await asyncio.sleep(5)
            
            except Exception as e:
                print(f"  Error processing image: {e}")
                continue
        
        return AgentResult(
            success=True,
            payload={"visual_concepts": visual_concepts}
        )
