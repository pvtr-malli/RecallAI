# RecallAI Quick Start

## Setup

```bash
# 1. Install uv
brew install uv

# 2. Install dependencies
uv sync

# 3. Install Ollama and pull model
brew install ollama
ollama serve  # In one terminal
ollama pull llama3.1:8b-instruct-q4_0  # In another terminal
```

## Run RecallAI (Single Command!)

```bash
python recall_ai/app.py
```

That's it! This starts **both** the API and UI in one process.

## Access

- **UI**: http://localhost:8000/
- **API Docs**: http://localhost:8000/docs

## Architecture

```
┌─────────────────────────────────────┐
│   Single Python Process             │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │   FastAPI    │  │   Gradio    │ │
│  │   (API)      │  │    (UI)     │ │
│  │   port 8000  │  │  mounted    │ │
│  │              │  │  on /       │ │
│  └──────────────┘  └─────────────┘ │
│                                     │
│  • Embedders loaded once at startup │
│  • Shared search processor          │
│  • Efficient memory usage           │
└─────────────────────────────────────┘
              ↓ API calls
┌─────────────────────────────────────┐
│        Ollama (External)            │
│     localhost:11434                 │
│  llama3.1:8b-instruct-q4_0         │
└─────────────────────────────────────┘
```

## Alternative: Run Components Separately

If you need to run them separately:

```bash
# API only
python recall_ai/gateway/start_server.py

# UI only (requires API running)
python recall_ai/ui/app.py
```
