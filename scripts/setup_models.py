#!/usr/bin/env python3
"""Download embedding models for RecallAI."""

import os
from pathlib import Path
from sentence_transformers import SentenceTransformer


def setup_models():
    """Download both embedding models."""
    # Set models directory
    models_dir = Path(__file__).parent.parent / "models"
    models_dir.mkdir(exist_ok=True)
    os.environ['SENTENCE_TRANSFORMERS_HOME'] = str(models_dir)

    print(f"Downloading models to: {models_dir}\n")

    # Download document model
    print("[1/2] Downloading document model (all-MiniLM-L6-v2)...")
    SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    print("✓ Done\n")

    # Download code model
    print("[2/2] Downloading code model (jina-embeddings-v2-base-code)...")
    SentenceTransformer("jinaai/jina-embeddings-v2-base-code")
    print("✓ Done\n")

    print("Setup complete!")


if __name__ == "__main__":
    setup_models()
