import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MISTRAL_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    PINECONE_API_KEY: str = ""
    PINECONE_ENV: str = "us-east-1"
    REDIS_URL: str = "redis://localhost:6379"
    GRAPH_STORAGE_PATH: str = "data/knowledge_graph.json"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
