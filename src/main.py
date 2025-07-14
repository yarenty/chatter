import os
import logging
logging.basicConfig(level=logging.CRITICAL, force=True)
logging.getLogger("backoff").setLevel(logging.CRITICAL)
logging.getLogger("posthog").setLevel(logging.CRITICAL)

os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"
os.environ["MEM0_TELEMETRY_ENABLED"] = "False"
os.environ["POSTHOG_API_KEY"] = ""
os.environ["OPENAI_API_KEY"] = ""

from monkeypatch_blockers import *

logger = logging.getLogger(__name__)

import argparse
from agent import ChatterAgent

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level', default='INFO', help='Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    args = parser.parse_args()
    # User log-level only for your own logs, not for suppressed libraries
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper(), logging.INFO))

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
