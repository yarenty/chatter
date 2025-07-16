from memory_base import BaseMemoryBackend
from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0.embeddings.configs import EmbedderConfig
from mem0.vector_stores.configs import VectorStoreConfig
from mem0.llms.configs import LlmConfig
from config import EMBEDDING_PROVIDER, EMBEDDING_MODEL, VECTOR_STORE_PROVIDER, LLM_PROVIDER, LLM_MODEL, CHROMA_DB_PATH
from typing import Any, List, Optional

class ChromaMem0Backend(BaseMemoryBackend):
    """
    Chroma/mem0-based memory backend implementation.
    """
    def __init__(self):
        memory_config = MemoryConfig(
            embedder=EmbedderConfig(provider=EMBEDDING_PROVIDER, config={"model": EMBEDDING_MODEL}),
            vector_store=VectorStoreConfig(provider=VECTOR_STORE_PROVIDER, config={"path": CHROMA_DB_PATH}),
            llm=LlmConfig(provider=LLM_PROVIDER, config={"model": LLM_MODEL})
        )
        self._memory = Memory(config=memory_config)

    @property
    def name(self) -> str:
        return "chroma_mem0"

    def search(self, query: str, agent_id: Optional[str] = None) -> List[Any]:
        return self._memory.search(query, agent_id=agent_id)

    def add(self, text: str, agent_id: Optional[str] = None) -> None:
        self._memory.add(text, agent_id=agent_id) 