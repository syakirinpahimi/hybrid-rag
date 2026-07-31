import os

from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


def init_settings() -> None:
    """Wire the configured LLM + embedding provider into LlamaIndex."""
    from llama_index.core import Settings

    if LLM_PROVIDER == "ollama":
        from llama_index.embeddings.ollama import OllamaEmbedding
        from llama_index.llms.ollama import Ollama

        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        Settings.llm = Ollama(
            model=os.getenv("OLLAMA_LLM", "llama3.1"),
            base_url=base_url,
            request_timeout=600.0,
            thinking=os.getenv("OLLAMA_THINKING", "false") == "true",
            num_output=1024,
        )
        Settings.embed_model = OllamaEmbedding(
            model_name=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
            base_url=base_url,
        )
    else:
        from llama_index.embeddings.openai import OpenAIEmbedding
        from llama_index.llms.openai import OpenAI

        Settings.llm = OpenAI(model="gpt-4o-mini")
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
