from abc import ABC, abstractmethod
from typing import Any, List, Optional

class BaseMemoryBackend(ABC):
    """
    Abstract base class for memory backends used in conversational agents.
    All memory solutions should inherit from this and implement the required methods.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Returns the name of the memory backend (for logging/benchmarking).
        """
        pass

    @abstractmethod
    def search(self, query: str, agent_id: Optional[str] = None) -> List[Any]:
        """
        Retrieve relevant memories for a given query.
        Args:
            query (str): The search query.
            agent_id (Optional[str]): Optional agent identifier.
        Returns:
            List[Any]: List of retrieved memories.
        """
        pass

    @abstractmethod
    def add(self, text: str, agent_id: Optional[str] = None) -> None:
        """
        Add a new memory to the backend.
        Args:
            text (str): The memory text to store.
            agent_id (Optional[str]): Optional agent identifier.
        """
        pass 