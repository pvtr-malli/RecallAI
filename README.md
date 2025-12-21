# RecallAI

**Intelligent local file search** - Search your documents and code using natural language, completely offline.

## Features

- 🔍 **Semantic Search** - Find files by meaning, not just keywords
- 🤖 **LLM Answers** - Get natural language answers from your content
- 💾 **Fully Local** - No cloud, no tracking, complete privacy
- ⚡ **Fast** - Pre-indexed embeddings for instant results
- 📝 **Multiple Formats** - `.txt`, `.md`, `.pdf`, `.py`, `.ipynb`

## Quick Start

### 1. Setup (One Time)

```bash
./setup.sh
```

This installs everything: `uv`, Ollama, Llama 3.1 model, and dependencies.

### 2. Run

```bash
source .venv/bin/activate
python recall_ai/app.py
```

### 3. Use

Open http://localhost:8000 in your browser.

1. **Configure Folders** - Add paths to index
2. **Index Files** - Click "Start Indexing"
3. **Search** - Ask questions in natural language

## Search Modes

- **Search Mode** - Returns matching files and chunks
- **Answer Mode** - Uses LLM to generate answers with sources

## Requirements

- Python 3.11+
- ~8GB RAM
- macOS or Linux

## Documentation

- [Quick Start Guide](QUICKSTART.md) - Detailed setup
- [API Documentation](docs/API.md) - REST API reference
- [Requirements](REQUIREMENTS.md) - Full project spec
- [Design Docs](docs/desings.md) - Architecture details

## Technology

- **Backend**: FastAPI + Gradio UI
- **Search**: FAISS (semantic vector search)
- **Embeddings**: Sentence Transformers
- **LLM**: Llama 3.1 8B via Ollama
- **Package Manager**: uv (fast Python installs)

## Makefile Commands

```bash
make setup   # One-time setup
make run     # Start RecallAI
make clean   # Clear indexes/models
make help    # Show all commands
```

## Architecture

```
┌────────────────────────────────────┐
│  RecallAI (Single Process)         │
│                                    │
│  FastAPI ────┬──── Gradio UI       │
│              │                     │
│  Search ─────┤                     │
│  Indexing ───┤                     │
│  Embeddings ─┘                     │
└────────────┬───────────────────────┘
             │
             ▼
        Ollama (LLM)
     localhost:11434
```

Everything runs locally. No data leaves your machine.

## Design Principles

- **Offline-first** - No cloud dependencies
- **Pre-indexed** - Embeddings computed upfront for speed
- **Incremental** - Only re-index changed files
- **Simple** - Clean API, no over-engineering

## Project Structure

```
recall_ai/
├── app.py              # Main entry point
├── gateway/            # FastAPI server & Gradio UI
├── processing/         # Search & LLM integration
├── embeddings/         # Vector search (FAISS)
├── parsers/            # File parsing & chunking
└── utils/              # Config, logging, scanning
```

## License

MIT

## Contributing

This is a learning project. Feel free to fork and experiment!
