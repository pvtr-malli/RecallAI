"""Code embedder for RecallAI using Jina code embeddings."""

import os
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from recall_ai.utils.logger import get_logger

logger = get_logger(__name__)


class CodeEmbedder:
    """
    Code embedder using Jina embeddings v2 base code model.
    Generates 768-dimensional embeddings for code.
    """

    def __init__(self, models_dir: Path) -> None:
        """
        Initialize code embedder.

        param models_dir: Directory to cache models.
        """
        self.models_dir = models_dir
        logger.info(f"Loading document embedding model from {models_dir}")
        os.environ['SENTENCE_TRANSFORMERS_HOME'] = str(models_dir)

        model_name = "jinaai/jina-embeddings-v2-base-code"

        self.model = SentenceTransformer(
            model_name,
            trust_remote_code=True
        )
        logger.info(f"Code embedding model loaded. Dimension: {self.model.get_sentence_embedding_dimension()}")

    def embed(self, texts: list[str]) -> np.ndarray:
        """
        Embed a list of code chunks.

        param texts: List of code chunks to embed.
        """
        logger.debug(f"Embedding {len(texts)} code chunks.")
        embeddings = self.model.encode(
            texts,
            show_progress_bar=False,
            normalize_embeddings=True
        )
        return embeddings

    def embed_single(self, text: str) -> np.ndarray:
        """
        Embed a single code chunk.

        param text: Code chunk to embed.
        """
        return self.embed([text])[0]
