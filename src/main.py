import argparse
import logging
from agent import ChatterAgent

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level', default='INFO', help='Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO), force=True)

    agent = ChatterAgent()
    print("Chatter Agent initialized. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        response = agent.chat(user_input)
        print(f"Agent: {response}")

if __name__ == "__main__":
    main()
