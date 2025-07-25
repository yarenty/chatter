"""
main.py
-------
Main entry point for the Chatter conversational agent application.

- Supports two backends: mem0 (default) and langchain.
- Handles argument parsing, logging configuration, and agent initialization.
- See config.py for backend and model configuration.
"""
import os
import logging

os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"
os.environ["MEM0_TELEMETRY_ENABLED"] = "False"
os.environ["POSTHOG_API_KEY"] = ""
os.environ["OPENAI_API_KEY"] = ""

from monkeypatch_blockers import *

logger = logging.getLogger(__name__)

import argparse

def main():
    """
    Main function for running the Chatter agent.
    Handles argument parsing, logging setup, and backend selection.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level', default='INFO', help='Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--backend', choices=['mem0', 'langchain'], default='mem0', help='Select backend: mem0 (default) or langchain')
    args = parser.parse_args()

    # Configure logging after parsing arguments
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO), format='%(asctime)s %(levelname)s %(message)s')
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper(), logging.INFO))
    logging.getLogger("lang_agent").setLevel(getattr(logging, args.log_level.upper(), logging.INFO))
    logging.getLogger("backoff").setLevel(logging.CRITICAL)
    logging.getLogger("posthog").setLevel(logging.CRITICAL)

    # Select backend and initialize agent
    if args.backend == 'langchain':
        from lang_agent import LangChatterAgent
        agent = LangChatterAgent()
    else:
        from agent import MemOChatterAgent
        agent = MemOChatterAgent()

    print(f"Chatter Agent initialized with backend '{args.backend}'. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        response = agent.chat(user_input)
        #print(f"Agent: {response}")

if __name__ == "__main__":
    main()
