from ..orchestrator.agent_base import BaseAgent, AgentResult
from ..tools.llm_clients import LLMClient
from ..tools.vector_store import VectorStore
from ..tools.graph_store import GraphStore
from typing import Dict, Any

class TeachingAgent(BaseAgent):
    name = "teaching_agent"

    def __init__(self):
        self.llm = LLMClient()
        self.vector_store = None
        self.graph_store = None

    async def run(self, context: Dict[str, Any]) -> AgentResult:
        query = context.get("query")
        if not query:
            return AgentResult(success=False, payload={"error": "No query provided"})

        if not self.vector_store: self.vector_store = VectorStore()
        if not self.graph_store: self.graph_store = GraphStore()

        # 1. Generate embedding for the query
        print(f"Generating embedding for query: {query[:50]}...")
        query_embedding = await self.llm.embed(query)
        
        # 2. Retrieve context from vector store
        print("Searching for relevant concepts...")
        results = self.vector_store.query(query_embedding, top_k=3)
        
        context_concepts = []
        context_text = ""
        
        if hasattr(results, 'matches') and len(results.matches) > 0:
            for match in results.matches:
                metadata = match.metadata
                context_text += f"Concept: {metadata['name']}\nDefinition: {metadata['definition']}\n\n"
                context_concepts.append(metadata['name'])
            print(f"Found {len(results.matches)} relevant concepts: {', '.join(context_concepts)}")
        else:
            context_text = "No relevant concepts found in the knowledge base."
            print("No relevant concepts found.")

        # 3. Generate explanation using retrieved context
        prompt = f"""
        You are a Socratic tutor. Use the following context to answer the student's question.
        
        Context from Knowledge Base:
        {context_text}
        
        Student Question: {query}
        
        Instructions:
        1. Provide a clear, accurate explanation based ONLY on the context provided
        2. If the context doesn't contain enough information, say so
        3. Ask a follow-up question to check understanding
        4. Be encouraging and supportive
        
        Format your response as:
        **Explanation:**
        [Your explanation here]
        
        **Follow-up Question:**
        [Your question here]
        """
        
        print("Generating tutor response...")
        response = await self.llm.generate(
            messages=[{"role": "user", "content": prompt}],
            provider="openrouter",
            model="google/gemma-3-27b-it:free",
            temperature=0.7
        )
        
        return AgentResult(
            success=True, 
            payload={
                "response": response, 
                "context_used": context_concepts,
                "context_text": context_text
            }
        )
