"""
lang_agent.py
-------------
Implements LangChatterAgent, a conversational agent using LangChain, Ollama, and ChromaDB for memory and LLM responses.

- Uses ChromaDB as a vector store for conversational memory.
- Integrates with Ollama for LLM-based responses.
- Configuration is loaded from config.py.
"""
import os
import logging
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
from config import OLLAMA_MODEL, CHROMA_DB_PATH

# Setup logging
logger = logging.getLogger(__name__)

class LangChatterAgent:
    """
    A conversational agent that uses LangChain for memory storage and retrieval, and Ollama for LLM-based responses.

    Attributes:
        vectorstore (Chroma): The ChromaDB vector store for storing and retrieving conversation history.
        embeddings (OllamaEmbeddings): Embedding model for vectorization.
        llm (ChatOllama): Ollama LLM for generating responses.
    """
    def __init__(self):
        """
        Initialize the LangChatterAgent.
        Sets up embeddings, vector store, and LLM using configuration from config.py.
        """
        logger.info("Initializing LangChatterAgent...")
        # Initialize Ollama Embeddings
        self.embeddings = OllamaEmbeddings(model=OLLAMA_MODEL)
        logger.debug("OllamaEmbeddings initialized with model: %s", OLLAMA_MODEL)

        # Initialize ChromaDB as a vector store
        self.vectorstore = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=self.embeddings)
        logger.debug("Chroma vectorstore initialized at: %s", CHROMA_DB_PATH)

        # Initialize Ollama Chat Model
        self.llm = ChatOllama(model=OLLAMA_MODEL)
        logger.debug("ChatOllama initialized with model: %s", OLLAMA_MODEL)

    def chat(self, user_message: str):
        """
        Process a user message, retrieve relevant memories, generate a response, and store the exchange.

        Args:
            user_message (str): The message from the user.
        Returns:
            str: The agent's response.
        """
        logger.info("Received user message: %s", user_message)
        # Retrieve relevant memories BEFORE adding the current user message
        relevant_memories = self.vectorstore.similarity_search(user_message, k=3)
        logger.info("Retrieved %d relevant memories.", len(relevant_memories))

        # Construct the prompt
        prompt = f"User: {user_message}\n"
        if relevant_memories:
            prompt += "Context from memory:\n"
            for mem in relevant_memories:
                prompt += f"- {mem.page_content}\n"
        prompt += "Agent:"
        logger.debug("Constructed prompt: %r", prompt)

        # Streaming response from Ollama
        print("Agent: ", end="", flush=True)
        response = ""
        logger.info("Starting streaming response from LLM...")
        for chunk in self.llm.stream(prompt):
            text = chunk.content if hasattr(chunk, 'content') else str(chunk)
            print(text, end="", flush=True)
            response += text
        print()  # Newline after streaming
        logger.info("Completed streaming response.")
        logger.debug("Full agent response: %r", response)

        # Store the user/agent exchange as a single memory
        exchange = f"User: {user_message}\nAgent: {response}"
        self.vectorstore.add_texts([exchange])
        logger.debug("Added user/agent exchange to vectorstore memory.")

        return response

if __name__ == "__main__":
    """
    Entry point for running the agent in interactive mode.
    """
    agent = LangChatterAgent()
    print("Chatter Agent initialized. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        response = agent.chat(user_input)
        print(f"Agent: {response}")