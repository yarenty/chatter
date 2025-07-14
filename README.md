# Chatter: An Agentic AI Chatbot with Memory

Chatter is a Python-based agentic AI chatbot that leverages LangChain for orchestration, Ollama for language model interactions, and ChromaDB for conversational memory.

## Features

- **Conversational Memory:** Utilizes ChromaDB as a vector store with LangChain's `VectorStoreRetrieverMemory` to store and recall past interactions, enabling more coherent and context-aware conversations.
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
    uv pip install langchain langchain-community chromadb ollama
    ```

## Configuration

The `src/config.py` file contains the main configuration for the Chatter agent.

- `OLLAMA_MODEL`: Specifies the Ollama model to use. Default is `llama3.2`.
- `CHROMA_DB_PATH`: Specifies the local directory where ChromaDB will persist its data. Default is `./chroma_db`.

  ```python
  # src/config.py
  OLLAMA_MODEL = "llama3.2"
  CHROMA_DB_PATH = "./chroma_db"
  ```

## Running the Chatbot

Chatter supports two backends:

- **mem0** (default): Uses the original memory backend.
- **LangChain**: Uses LangChain, Ollama, and ChromaDB for memory and LLM.

### To use the default (mem0) backend:
```bash
python src/main.py --backend=mem0
```

### To use the LangChain backend:
```bash
python src/main.py --backend=langchain
```

Once the agent is initialized, you can start chatting. Type `exit` to quit the application.

### Logging
You can control the logging level (for debug/info output) with the `--log-level` argument or the `CHATTER_LOG_LEVEL` environment variable:

```bash
python src/main.py --backend=langchain --log-level=DEBUG
# or
export CHATTER_LOG_LEVEL=DEBUG
python src/main.py --backend=langchain
```

### Resetting/Clearing ChromaDB Memory
To completely reset the LangChain agent's memory, delete the ChromaDB directory (by default `./chroma_db`):

```bash
rm -rf ./chroma_db
```
This will remove all stored conversation history for the LangChain backend.

## Project Structure

```
chatter/
├── .venv/                # Python virtual environment
├── src/
│   ├── __init__.py
│   ├── agent.py          # Core agent logic (mem0 backend)
│   ├── lang_agent.py     # LangChain, Ollama, ChromaDB integration (langchain backend)
│   ├── config.py         # Configuration settings
│   └── main.py           # Main application entry point
├── pyproject.toml        # Project dependencies and metadata
├── .gitignore            # Git ignore file
├── chroma_db/            # Directory for ChromaDB persistence (created on first run)
└── README.md             # Project documentation
```

## Future Enhancements

- Integration with more advanced tools and APIs.
- Support for different memory backends in LangChain.
- Web interface for easier interaction.
- More sophisticated prompt engineering and agentic behaviors.