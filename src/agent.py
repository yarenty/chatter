from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0.embeddings.configs import EmbedderConfig
from mem0.vector_stores.configs import VectorStoreConfig
from mem0.llms.configs import LlmConfig
import ollama
# from config import OLLAMA_MODEL  # Remove this line

class ChatterAgent:
    def __init__(self, agent_id="chatter-agent"):
        memory_config = MemoryConfig(
            embedder=EmbedderConfig(provider="ollama", config={"model": "llama3.2"}),
            vector_store=VectorStoreConfig(provider="chroma", config={}),
            llm=LlmConfig(provider="ollama", config={"model": "llama3.2"})
        )
        #embedding_backend="sentence-transformers",
        #embedding_model="all-MiniLM-L6-v2",
        self.memory = Memory(config=memory_config)
        self.agent_id = agent_id

    def chat(self, user_message: str):
        # Store the user message in memory
        self.memory.add(user_message, agent_id=self.agent_id)

        # Retrieve relevant memories
        relevant_memories = self.memory.search(user_message, agent_id=self.agent_id)
        
        # Construct the prompt for Ollama, including relevant memories
        prompt = f"User: {user_message}\n"
        if relevant_memories:
            prompt += "Context from memory:\n"
            for mem in relevant_memories:
                if isinstance(mem, dict) and 'memory' in mem:
                    prompt += f"- {mem['memory']}\n"
                else:
                    prompt += f"- {mem}\n"
        prompt += "Agent:"

        # Get response from Ollama
        response = ollama.chat(model="llama3.2", messages=[{'role': 'user', 'content': prompt}])
        agent_response = response['message']['content']

        # Store the agent's response in memory
        self.memory.add(agent_response, agent_id=self.agent_id)

        return agent_response

if __name__ == "__main__":
    agent = ChatterAgent()
    print("Chatter Agent initialized. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        
        response = agent.chat(user_input)
        print(f"Agent: {response}")
