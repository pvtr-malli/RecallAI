"""Document embedder using SBERT."""

import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np
from recall_ai.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentEmbedder:
    """
    Document embedder using SBERT model.
    """

    def __init__(self, models_dir: Path = Path("models")) -> None:
        """
        Initialize document embedder.

        param models_dir: Directory containing the model files.
        """
        logger.info(f"Loading document embedding model from {models_dir}")
        os.environ['SENTENCE_TRANSFORMERS_HOME'] = str(models_dir)
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.dimension = 384  # SBERT dimension.
        logger.info("Document embedder initialized.")

    def embed(self, texts: list[str]) -> np.ndarray:
        """
        Generate embeddings for text chunks.

        param texts: List of text chunks to embed.
        """
        logger.debug(f"Generating embeddings for {len(texts)} chunks.")
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings

    def embed_single(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.

        param text: Text to embed.
        """
        return self.embed([text])[0]
