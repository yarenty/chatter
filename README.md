# Chatter: An Agentic AI Chatbot with Memory

Chatter is a Python-based agentic AI chatbot that leverages Ollama for language model interactions and Mem0 for conversational memory.

## Features

- **Conversational Memory:** Utilizes Mem0 to store and recall past interactions, enabling more coherent and context-aware conversations.
- **Ollama Integration:** Connects with local or remote Ollama instances to use various large language models (defaulting to `llama3.2`).
- **Modular Design:** Separated configuration, agent logic, and main application for easy extension and maintenance.

## Setup and Installation

Follow these steps to get Chatter up and running on your local machine.

### Prerequisites

- **Python 3.9+:** Ensure you have a compatible Python version installed.
- **uv:** A fast Python package installer and resolver. If you don't have it, install it:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Ollama:** Download and install Ollama from [ollama.com](https://ollama.com/). Make sure to pull the `llama3.2` model:
  ```bash
  ollama pull llama3.2
  ```

### Installation Steps

1.  **Clone the repository (if applicable) or navigate to the project directory:**
    ```bash
    cd /path/to/chatter
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    uv venv
    source .venv/bin/activate
    uv pip install -e .
    ```
    *Note: The `-e .` installs the project in editable mode, which is useful for development. If you encounter issues with `mem0` installation, you might need to install it directly from its GitHub repository:* `uv pip install git+https://github.com/mem0ai/mem0.git`

## Configuration

The `src/config.py` file contains the main configuration for the Chatter agent.

- `OLLAMA_MODEL`: Specifies the Ollama model to use. Default is `llama3.2`.

  ```python
  # src/config.py
  OLLAMA_MODEL = "llama3.2"
  ```

## Running the Chatbot

To start the Chatter agent, run the `main.py` script:

```bash
python src/main.py
```

Once the agent is initialized, you can start chatting. Type `exit` to quit the application.

## Project Structure

```
chatter/
├── .venv/                # Python virtual environment
├── src/
│   ├── __init__.py
│   ├── agent.py          # Core agent logic (Ollama and Mem0 integration)
│   ├── config.py         # Configuration settings
│   └── main.py           # Main application entry point
├── pyproject.toml        # Project dependencies and metadata
├── .gitignore            # Git ignore file
└── README.md             # Project documentation
```

## Future Enhancements

- Integration with more advanced tools and APIs.
- Support for different memory backends in Mem0.
- Web interface for easier interaction.
- More sophisticated prompt engineering and agentic behaviors.
