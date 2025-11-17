from pinecone import Pinecone, ServerlessSpec
from ..orchestrator.config import settings
import time

class VectorStore:
    def __init__(self, index_name="flowmind-concepts"):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = index_name
        
        # Check if index exists, if not create it (serverless)
        indexes = self.pc.list_indexes()
        existing_names = [i.name for i in indexes]
        
        if index_name not in existing_names:
            print(f"Creating index {index_name}...")
            self.pc.create_index(
                name=index_name,
                dimension=1024, 
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=settings.PINECONE_ENV
                )
            )
            while not self.pc.describe_index(index_name).status['ready']:
                time.sleep(1)
        
        self.index = self.pc.Index(index_name)
        print(f"Pinecone Index Host: {self.index._config.host if hasattr(self.index, '_config') else 'Unknown'}")

    def upsert(self, vectors):
        # vectors: list of (id, values, metadata)
        return self.index.upsert(vectors=vectors)

    def query(self, vector, top_k=5, filter=None):
        return self.index.query(vector=vector, top_k=top_k, include_metadata=True, filter=filter)
