from ..orchestrator.agent_base import BaseAgent, AgentResult
from ..tools.pdf_parser import PDFParser
from typing import Dict, Any

class ParsingAgent(BaseAgent):
    name = "parsing_agent"

    def __init__(self):
        self.parser = PDFParser()

    async def run(self, context: Dict[str, Any]) -> AgentResult:
        pdf_path = context.get("pdf_path")
        if not pdf_path:
            return AgentResult(success=False, payload={"error": "No PDF path provided"})

        try:
            blocks = self.parser.parse(pdf_path)
            return AgentResult(success=True, payload={"blocks": blocks})
        except Exception as e:
            return AgentResult(success=False, payload={"error": str(e)})
