"""FAISS index manager for RecallAI."""

from pathlib import Path
import faiss
import numpy as np
from recall_ai.utils.logger import get_logger

logger = get_logger(__name__)


class FAISSManager:
    """
    Manager for FAISS vector index.
    """

    def __init__(self, dimension: int, index_path: Path) -> None:
        """
        Initialize FAISS manager.

        param dimension: Dimension of the embeddings.
        param index_path: Path to save/load the FAISS index.
        """
        self.dimension = dimension
        self.index_path = index_path
        self.index = self._load_or_create_index()

    def _load_or_create_index(self) -> faiss.Index:
        """
        Load existing index or create new one.
        """
        if self.index_path.exists():
            logger.info(f"Loading existing FAISS index from {self.index_path}")
            return faiss.read_index(str(self.index_path))
        else:
            logger.info(f"Creating new FAISS HNSW index with dimension {self.dimension}")
            index = faiss.IndexHNSWFlat(self.dimension, 32)
            index.hnsw.efConstruction = 30 # Search depth during index building (higher = better quality).
            index.hnsw.efSearch = 25  # Query time search depth.
            return index

    def add_vectors(self, vectors: np.ndarray) -> None:
        """
        Add vectors to the index.

        param vectors: Numpy array of vectors to add.
        """
        logger.debug(f"Adding {len(vectors)} vectors to FAISS index.")
        self.index.add(vectors.astype(np.float32))

    def search(self, query_vector: np.ndarray, k: int = 5) -> tuple[np.ndarray, np.ndarray]:
        """
        Search for similar vectors.

        param query_vector: Query vector.
        param k: Number of results to return.
        """
        distances, indices = self.index.search(
            query_vector.astype(np.float32).reshape(1, -1), k
        )
        return distances[0], indices[0]

    def save(self) -> None:
        """
        Save index to disk.
        """
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Saving FAISS index to {self.index_path}")
        faiss.write_index(self.index, str(self.index_path))
        logger.info("FAISS index saved successfully.")

    def get_count(self) -> int:
        """
        Get number of vectors in index.
        """
        return self.index.ntotal

    def reset(self) -> None:
        """
        Reset index to empty state.
        """
        logger.info("Resetting FAISS index.")
        self.index = faiss.IndexHNSWFlat(self.dimension, 32)
        self.index.hnsw.efConstruction = 30
        self.index.hnsw.efSearch = 25
