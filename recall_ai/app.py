"""RecallAI - Single application entry point with both API and UI."""

import gradio as gr
from fastapi import FastAPI
from pathlib import Path
import uvicorn

from recall_ai.gateway.start_server import app as fastapi_app
from recall_ai.ui.app import create_interface

# Mount Gradio UI on FastAPI app
ui = create_interface()
app = gr.mount_gradio_app(fastapi_app, ui, path="/")


def main():
    """Start RecallAI with both API and UI."""
    print("=" * 60)
    print("🚀 Starting RecallAI")
    print("=" * 60)
    print()
    print("📡 API endpoints available at: http://localhost:8000/docs")
    print("🖥️  UI available at: http://localhost:8000/")
    print()
    print("💡 Make sure Ollama is running: ollama serve")
    print("=" * 60)
    print()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()
