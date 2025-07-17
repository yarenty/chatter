from memory_base import BaseMemoryBackend
from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0.embeddings.configs import EmbedderConfig
from mem0.graphs.configs import GraphStoreConfig
from mem0.llms.configs import LlmConfig
from config import EMBEDDING_PROVIDER, EMBEDDING_MODEL, LLM_PROVIDER, LLM_MODEL
from typing import Any, List, Optional

class ZeroGMem0Backend(BaseMemoryBackend):
    """
    Mem0ᵍ/Neo4j-based memory backend using mem0's graph storage.
    Requires Neo4j running and accessible at the configured URI.
    """
    def __init__(self):
        memory_config = MemoryConfig(
            embedder=EmbedderConfig(provider=EMBEDDING_PROVIDER, config={"model": EMBEDDING_MODEL}),
            vector_store=GraphStoreConfig(
                provider="neo4j",
                config={
                    "uri": "bolt://localhost:7687",
                    "user": "neo4j",
                    "password": "your_password",  # <-- Set your Neo4j password here
                }
            ),
            llm=LlmConfig(provider=LLM_PROVIDER, config={"model": LLM_MODEL})
        )
        self._memory = Memory(config=memory_config)

    @property
    def name(self) -> str:
        return "zerog_mem0"

    def search(self, query: str, agent_id: Optional[str] = None) -> List[Any]:
        return self._memory.search(query, agent_id=agent_id)

    def add(self, text: str, agent_id: Optional[str] = None) -> None:
        self._memory.add(text, agent_id=agent_id)

    def update(self, *args, **kwargs):
        raise NotImplementedError("Update is disabled for append-only backend.")

    def delete(self, *args, **kwargs):
        raise NotImplementedError("Delete is disabled for append-only backend.") 