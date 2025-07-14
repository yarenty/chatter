# Chatter: An Agentic AI Chatbot with Memory

Chatter is a Python-based agentic AI chatbot that leverages Ollama for language model interactions and Mem0 for conversational memory.

## Features

- **Conversational Memory:** Utilizes Mem0 to store and recall past interactions, enabling more coherent and context-aware conversations.
- **Ollama Integration:** Connects with local or remote Ollama instances to use various large language models (defaulting to `llama3.2`).
- **Modular Design:** Separated configuration, agent logic, and main application for easy extension and maintenance.
- **Configurable Logging:** Set the logging level from the command line for easier debugging and development.

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
- **ChromaDB:** Used for local vector storage. Install with:
  ```bash
  pip install chromadb
  ```
- **mem0:** Memory backend. Install from PyPI or directly from GitHub for the latest version:
  ```bash
  pip install mem0ai
  # or for latest
  pip install git+https://github.com/mem0ai/mem0.git
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

All model and backend configuration is in `src/config.py`:

```python
# src/config.py
OLLAMA_MODEL = "llama3.2"
EMBEDDING_PROVIDER = "ollama"
EMBEDDING_MODEL = "llama3.2"
VECTOR_STORE_PROVIDER = "chroma"
LLM_PROVIDER = "ollama"
LLM_MODEL = "llama3.2"
```

You can change these values to use different models or backends as needed.

## Running the Chatbot

To start the Chatter agent, run the `main.py` script:

```bash
python src/main.py
```

### Logging Level

You can control the logging verbosity from the command line:

```bash
python src/main.py --log-level DEBUG
```

Supported levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` (default: `INFO`).

## Memory Storage Locations

- **Chroma Vector Store:**
  - By default, Chroma stores its data in a `./chroma/` directory in your project root. You can change this by setting the `path` in the Chroma config in `src/config.py`.
- **mem0 History Database:**
  - mem0 uses a local SQLite database at `~/.mem0/history.db` by default for storing conversation history.

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
