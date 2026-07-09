"""File processor for RecallAI - handles processing of different file types."""

from pathlib import Path
from typing import Tuple

from recall_ai.parsers.document_parser import parse_document
from recall_ai.parsers.code_parser import parse_code
from recall_ai.parsers.notebook_parser import parse_notebook
from recall_ai.parsers.chunker import chunk_text, chunk_code
from recall_ai.embeddings.document_embedder import DocumentEmbedder
from recall_ai.embeddings.code_embedder import CodeEmbedder
from recall_ai.embeddings.faiss_manager import FAISSManager
from recall_ai.embeddings.metadata_store import MetadataStore
from recall_ai.utils.hash_utils import compute_file_hash
from recall_ai.utils.logger import get_logger

logger = get_logger(__name__)


def process_document_file(
    file_path: Path,
    metadata_store: MetadataStore,
    doc_embedder: DocumentEmbedder,
    doc_faiss: FAISSManager,
    current_doc_faiss_index: int
) -> int:
    """
    Process a document file (.txt, .md, .pdf).

    param file_path: Path to document file.
    param metadata_store: Metadata store instance.
    param doc_embedder: Document embedder instance.
    param doc_faiss: Document FAISS manager instance.
    param current_doc_faiss_index: Current FAISS index position.
    return: Updated FAISS index position.
    """
    logger.info(f"Processing document: {file_path}")

    # Compute file hash for change detection.
    file_hash = compute_file_hash(file_path)
    last_modified = file_path.stat().st_mtime

    # Check if file already indexed and unchanged.
    existing_file = metadata_store.get_file_by_path(str(file_path))
    if existing_file and existing_file["file_hash"] == file_hash:
        logger.info(f"Skipping unchanged file: {file_path.name}")
        return current_doc_faiss_index

    # Delete old chunks from metadata if file was previously indexed.
    # Note: FAISS doesn't support vector deletion, so old vectors remain.
    # Use rebuild=True to clear orphaned vectors periodically.
    if existing_file:
        logger.info(f"Removing old chunk metadata for updated file: {file_path.name}")
        metadata_store.delete_file(str(file_path))

    # Parse document.
    text = parse_document(file_path)

    # Chunk text with file extension for document-aware splitting.
    chunks = chunk_text(text, file_extension=file_path.suffix)
    logger.info(f"Created {len(chunks)} chunks from {file_path.name}")

    # Generate embeddings.
    embeddings = doc_embedder.embed(chunks)

    # Add file metadata.
    file_id = metadata_store.add_file(
        file_path=str(file_path),
        file_type="document",
        file_hash=file_hash,
        last_modified=last_modified
    )

    # Add vectors to FAISS and store chunk metadata.
    doc_faiss.add_vectors(embeddings)
    for i, chunk in enumerate(chunks):
        metadata_store.add_chunk(
            file_id=file_id,
            chunk_index=i,
            chunk_text=chunk,
            faiss_index=current_doc_faiss_index
        )
        current_doc_faiss_index += 1

    return current_doc_faiss_index


def process_code_file(
    file_path: Path,
    metadata_store: MetadataStore,
    code_embedder: CodeEmbedder,
    code_faiss: FAISSManager,
    current_code_faiss_index: int
) -> int:
    """
    Process a code file (.py).

    param file_path: Path to code file.
    param metadata_store: Metadata store instance.
    param code_embedder: Code embedder instance.
    param code_faiss: Code FAISS manager instance.
    param current_code_faiss_index: Current FAISS index position.
    return: Updated FAISS index position.
    """
    logger.info(f"Processing code file: {file_path}")

    # Compute file hash for change detection.
    file_hash = compute_file_hash(file_path)
    last_modified = file_path.stat().st_mtime

    # Check if file already indexed and unchanged.
    existing_file = metadata_store.get_file_by_path(str(file_path))
    if existing_file and existing_file["file_hash"] == file_hash:
        logger.info(f"Skipping unchanged file: {file_path.name}")
        return current_code_faiss_index

    # Delete old chunks from metadata if file was previously indexed.
    if existing_file:
        logger.info(f"Removing old chunk metadata for updated file: {file_path.name}")
        metadata_store.delete_file(str(file_path))

    # Parse code file.
    code = parse_code(file_path)

    # Chunk code using code-aware chunking.
    chunks = chunk_code(code, file_extension=file_path.suffix)
    logger.info(f"Created {len(chunks)} chunks from {file_path.name}")

    # Generate embeddings.
    embeddings = code_embedder.embed(chunks)

    # Add file metadata.
    file_id = metadata_store.add_file(
        file_path=str(file_path),
        file_type="code",
        file_hash=file_hash,
        last_modified=last_modified
    )

    # Add vectors to FAISS and store chunk metadata.
    code_faiss.add_vectors(embeddings)
    for i, chunk in enumerate(chunks):
        metadata_store.add_chunk(
            file_id=file_id,
            chunk_index=i,
            chunk_text=chunk,
            faiss_index=current_code_faiss_index
        )
        current_code_faiss_index += 1

    return current_code_faiss_index


def process_notebook_file(
    file_path: Path,
    metadata_store: MetadataStore,
    doc_embedder: DocumentEmbedder,
    doc_faiss: FAISSManager,
    code_embedder: CodeEmbedder,
    code_faiss: FAISSManager,
    current_doc_faiss_index: int,
    current_code_faiss_index: int
) -> Tuple[int, int]:
    """
    Process a notebook file (.ipynb).
    Processes markdown cells through document flow and code cells through code flow.

    param file_path: Path to notebook file.
    param metadata_store: Metadata store instance.
    param doc_embedder: Document embedder instance.
    param doc_faiss: Document FAISS manager instance.
    param code_embedder: Code embedder instance.
    param code_faiss: Code FAISS manager instance.
    param current_doc_faiss_index: Current document FAISS index position.
    param current_code_faiss_index: Current code FAISS index position.
    return: Tuple of (updated doc FAISS index, updated code FAISS index).
    """
    logger.info(f"Processing notebook: {file_path}")

    # Compute file hash for change detection.
    file_hash = compute_file_hash(file_path)
    last_modified = file_path.stat().st_mtime

    # Check if file already indexed and unchanged.
    existing_file = metadata_store.get_file_by_path(str(file_path))
    if existing_file and existing_file["file_hash"] == file_hash:
        logger.info(f"Skipping unchanged file: {file_path.name}")
        return current_doc_faiss_index, current_code_faiss_index

    # Delete old chunks from metadata if file was previously indexed.
    if existing_file:
        logger.info(f"Removing old chunk metadata for updated file: {file_path.name}")
        metadata_store.delete_file(str(file_path))

    # Parse notebook into cells.
    cells = parse_notebook(file_path)
    if not cells:
        logger.info(f"No cells to process in {file_path.name}")
        return current_doc_faiss_index, current_code_faiss_index

    # Add file metadata.
    file_id = metadata_store.add_file(
        file_path=str(file_path),
        file_type="notebook",
        file_hash=file_hash,
        last_modified=last_modified
    )

    # Process each cell based on its type.
    for cell in cells:
        if cell.cell_type == "markdown":
            # Process markdown cells through document flow.
            chunks = chunk_text(cell.content, file_extension=".md")
            embeddings = doc_embedder.embed(chunks)

            # Add vectors to document FAISS index.
            doc_faiss.add_vectors(embeddings)
            for i, chunk in enumerate(chunks):
                metadata_store.add_chunk(
                    file_id=file_id,
                    chunk_index=cell.cell_index * 1000 + i,  # Unique index per cell.
                    chunk_text=chunk,
                    faiss_index=current_doc_faiss_index
                )
                current_doc_faiss_index += 1

        elif cell.cell_type == "code":
            # Process code cells through code flow.
            chunks = chunk_code(cell.content, file_extension=".py")
            embeddings = code_embedder.embed(chunks)

            # Add vectors to code FAISS index.
            code_faiss.add_vectors(embeddings)
            for i, chunk in enumerate(chunks):
                metadata_store.add_chunk(
                    file_id=file_id,
                    chunk_index=cell.cell_index * 1000 + i,  # Unique index per cell.
                    chunk_text=chunk,
                    faiss_index=current_code_faiss_index
                )
                current_code_faiss_index += 1
    logger.info("*"*48)
    logger.info(f"Processed {len(cells)} cells from {file_path.name}")
    return current_doc_faiss_index, current_code_faiss_index
