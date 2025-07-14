"""
agent.py
---------
Implements MemOChatterAgent, a memory-augmented conversational agent using the mem0 library for vector storage and retrieval, and Ollama for LLM responses.

- Stores and retrieves conversational context using a vector store (ChromaDB by default).
- Integrates with Ollama for generating agent responses.
- Configuration is loaded from config.py.
"""
import logging
from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0.embeddings.configs import EmbedderConfig
from mem0.vector_stores.configs import VectorStoreConfig
from mem0.llms.configs import LlmConfig
import ollama
from config import EMBEDDING_PROVIDER, EMBEDDING_MODEL, VECTOR_STORE_PROVIDER, LLM_PROVIDER, LLM_MODEL, CHROMA_DB_PATH

# Remove logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemOChatterAgent:
    """
    A conversational agent that uses mem0 for memory storage and retrieval, and Ollama for LLM-based responses.

    Attributes:
        memory (Memory): The memory backend for storing and retrieving conversation history.
        agent_id (str): Unique identifier for the agent instance.
    """
    def __init__(self, agent_id="chatter-agent"):
        """
        Initialize the MemOChatterAgent.

        Args:
            agent_id (str): Unique identifier for the agent. Default is 'chatter-agent'.
        """
        # Configure memory with embedding, vector store, and LLM settings from config.py
        memory_config = MemoryConfig(
            embedder=EmbedderConfig(provider=EMBEDDING_PROVIDER, config={"model": EMBEDDING_MODEL}),
            vector_store=VectorStoreConfig(provider=VECTOR_STORE_PROVIDER, config={"path": CHROMA_DB_PATH}),
            llm=LlmConfig(provider=LLM_PROVIDER, config={"model": LLM_MODEL})
        )
        self.memory = Memory(config=memory_config)
        self.agent_id = agent_id

    def chat(self, user_message: str):
        """
        Process a user message, retrieve relevant memories, generate a response, and store the exchange.

        Args:
            user_message (str): The message from the user.
        Returns:
            str: The agent's response.
        """
        logger.info(f"user_message = {user_message}")
        # Retrieve relevant memories before adding the current message
        relevant_memories = None
        try:
            relevant_memories = self.memory.search(user_message, agent_id=self.agent_id)
            logger.debug(f"relevant_memories = {relevant_memories}")
            logger.info(f"Retrieved {len(relevant_memories) if relevant_memories else 0} relevant memories.")
        except Exception as e:
            logger.exception("Exception during memory.search:")
            relevant_memories = []
        # Construct the prompt for Ollama, including relevant memories
        prompt = f"User: {user_message}\n"
        if relevant_memories:
            prompt += "Context from memory:\n"
            for mem in relevant_memories:
                # Each memory may be a dict or string, handle accordingly
                if isinstance(mem, dict) and 'memory' in mem:
                    prompt += f"- {mem['memory']}\n"
                else:
                    prompt += f"- {mem}\n"
        prompt += "Agent:"

        # Stream response from Ollama LLM
        try:
            response_stream = ollama.chat(model=LLM_MODEL, messages=[{'role': 'user', 'content': prompt}], stream=True)
            agent_response = ""
            print("Agent: ", end="", flush=True)
            for chunk in response_stream:
                content = chunk['message']['content']
                print(content, end="", flush=True)
                agent_response += content
            print()  # Newline after streaming
        except Exception as e:
            logger.exception("Exception during ollama.chat:")
            agent_response = "[Error generating response]"

        # Store the user/agent exchange as a single memory
        exchange = f"User: {user_message}\nAgent: {agent_response}"
        try:
            self.memory.add(exchange, agent_id=self.agent_id)
        except Exception as e:
            logger.exception("Exception during memory.add (agent response):")
        return agent_response

if __name__ == "__main__":
    """
    Entry point for running the agent in interactive mode.
    """
    agent = MemOChatterAgent()
    print("Chatter Agent initialized. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        response = agent.chat(user_input)
        print(f"Agent: {response}")
