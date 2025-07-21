from memory_base import BaseMemoryBackend
from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0.embeddings.configs import EmbedderConfig
from mem0.graphs.configs import GraphStoreConfig
from mem0.vector_stores.configs import VectorStoreConfig
from mem0.llms.configs import LlmConfig
from config import EMBEDDING_PROVIDER, EMBEDDING_MODEL, VECTOR_STORE_PROVIDER, LLM_PROVIDER, LLM_MODEL, CHROMA_DB_PATH
from typing import Any, List, Optional

class ZeroGBackend(BaseMemoryBackend):
    """
    Mem0ᵍ/Neo4j-based memory backend using mem0's graph storage.
    Requires Neo4j running and accessible at the configured URI.
    """
    def __init__(self):
        memory_config = MemoryConfig(
            embedder=EmbedderConfig(provider=EMBEDDING_PROVIDER, config={"model": EMBEDDING_MODEL}),
            graph_store=GraphStoreConfig(
                provider="neo4j",
                config={
                    "url": "bolt://localhost:7687",
                    "username": "neo4j",
                    "password": "q1w2e3r4t5",  # <-- Set your Neo4j password here
                }
            ),
            # vector_store=VectorStoreConfig(provider=VECTOR_STORE_PROVIDER, config={"path": CHROMA_DB_PATH}),
            # Explicitly configure a vector store to avoid the default ChromaDB with the filtering bug.
            # Using in-memory Qdrant as a replacement.
            vector_store=VectorStoreConfig(
                provider="qdrant",
                config={
                    "on_disk": False,
                    "embedding_model_dims": 3072
                }
            ),
            llm=LlmConfig(provider=LLM_PROVIDER, config={"model": LLM_MODEL})
        )
        self._memory = Memory(config=memory_config)

    @property
    def name(self) -> str:
        return "zerog_mem0"

    def search(self, query: str, agent_id: Optional[str] = None) -> List[Any]:
        return self._memory.search(query, agent_id=agent_id, user_id="")

    def add(self, text: str, agent_id: Optional[str] = None) -> None:
        # Always pass a non-empty user_id to avoid KeyError in mem0
        self._memory.add(text, agent_id=agent_id, user_id="")

    def update(self, *args, **kwargs):
        raise NotImplementedError("Update is disabled for append-only backend.")

    def delete(self, *args, **kwargs):
        raise NotImplementedError("Delete is disabled for append-only backend.") 