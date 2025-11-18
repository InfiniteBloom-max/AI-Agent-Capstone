from ..orchestrator.agent_base import BaseAgent, AgentResult
from ..tools.llm_clients import LLMClient
from typing import Dict, Any

class CriticAgent(BaseAgent):
    name = "critic_agent"

    def __init__(self):
        self.llm = LLMClient()

    async def run(self, context: Dict[str, Any]) -> AgentResult:
        proposed_response = context.get("proposed_response")
        source_context = context.get("source_context")
        
        if not proposed_response:
            return AgentResult(success=False, payload={"error": "No response to critique"})

        prompt = f"""
        Critique the following tutor response based on the provided source context.
        Check for:
        1. Hallucinations (facts not in context)
        2. Tone (should be encouraging but rigorous)
        3. Clarity
        
        Source Context:
        {source_context}
        
        Tutor Response:
        {proposed_response}
        
        Return 'APPROVED' if good, or a critique explaining what to fix.
        """
        
        critique = await self.llm.generate(
            messages=[{"role": "user", "content": prompt}],
            provider="mistral",
            temperature=0.0
        )
        
        is_approved = "APPROVED" in critique
        
        return AgentResult(success=True, payload={"approved": is_approved, "critique": critique})
