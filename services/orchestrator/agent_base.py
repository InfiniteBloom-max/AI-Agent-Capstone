from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

@dataclass
class AgentResult:
    success: bool
    payload: Dict[str, Any]
    meta: Dict[str, Any] = field(default_factory=dict)

class BaseAgent:
    name: str = "base_agent"

    async def run(self, context: Dict[str, Any]) -> AgentResult:
        raise NotImplementedError

    async def validate(self, result: AgentResult) -> bool:
        return True
