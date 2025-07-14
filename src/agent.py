from mem0 import Memory
import ollama
from config import OLLAMA_MODEL

class ChatterAgent:
    def __init__(self):
        self.memory = Memory()

    def chat(self, user_message: str):
        # Store the user message in memory
        self.memory.add(user_message)

        # Retrieve relevant memories
        relevant_memories = self.memory.recall(user_message)
        
        # Construct the prompt for Ollama, including relevant memories
        prompt = f"User: {user_message}\n"
        if relevant_memories:
            prompt += "Context from memory:\n"
            for mem in relevant_memories:
                prompt += f"- {mem.text}\n"
        prompt += "Agent:"

        # Get response from Ollama
        response = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}])
        agent_response = response['message']['content']

        # Store the agent's response in memory
        self.memory.add(agent_response)

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
