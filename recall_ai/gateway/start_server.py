#!/usr/bin/env python3
"""Start the RecallAI FastAPI server."""

import uvicorn
import yaml
from pathlib import Path
from fastapi import FastAPI

from recall_ai.utils.config import load_config
from recall_ai.utils.scanner import scan_files
from recall_ai.utils.scanner import classify_file, FileType
from recall_ai.embeddings.document_embedder import DocumentEmbedder
from recall_ai.embeddings.code_embedder import CodeEmbedder
from recall_ai.embeddings.faiss_manager import FAISSManager
from recall_ai.embeddings.metadata_store import MetadataStore
from recall_ai.processing.file_processor import (
    process_document_file,
    process_code_file,
    process_notebook_file
)
from recall_ai.processing.search_processor import SearchProcessor
from recall_ai.gateway.models import (
    UpdateFoldersRequest,
    UpdateFoldersResponse,
    IndexResponse,
    SearchRequest
)
from recall_ai.utils.logger import get_logger

logger = get_logger(__name__)


app = FastAPI(title="RecallAI", description="Intelligent local file search system.")


# Initialize search processor once at module load time
def _initialize_search_processor():
    """Initialize search processor on module load."""
    logger.info("Initializing search processor")
    project_root = Path(__file__).parent.parent.parent
    config_path = project_root / "config.yaml"
    config = load_config(config_path)

    models_dir = (project_root / config.models_dir).resolve()
    indexes_dir = (project_root / config.indexes_dir).resolve()
    db_path = (project_root / config.db_path).resolve()

    processor = SearchProcessor(
        models_dir=models_dir,
        indexes_dir=indexes_dir,
        db_path=db_path
    )
    logger.info("Search processor initialized and ready")
    return processor


# Global search processor instance
search_processor = _initialize_search_processor()


@app.post("/index", response_model=IndexResponse)
def index_files(rebuild: bool = False) -> IndexResponse:
    """
    Index files from configured folders.

    param rebuild: If True, clear existing index and rebuild from scratch.
    """
    logger.info("Starting indexing process.")
    project_root = Path(__file__).parent.parent.parent
    config_path = project_root / "config.yaml"
    config = load_config(config_path)

    # Scan files.
    files = scan_files(config.indexing)
    logger.info(f"Found {len(files)} files to process.")

    # Initialize embedders, FAISS indexes, and metadata store.
    logger.info("Initializing embedders, FAISS indexes, and metadata store.")

    # Resolve absolute paths from project root.
    models_dir = (project_root / config.models_dir).resolve()
    indexes_dir = (project_root / config.indexes_dir).resolve()
    db_path = (project_root / config.db_path).resolve()

    logger.info(f"Using models_dir: {models_dir}")
    logger.info(f"Using indexes_dir: {indexes_dir}")
    logger.info(f"Using db_path: {db_path}")

    # Document embedder and FAISS index (384-dimensional).
    doc_embedder = DocumentEmbedder(models_dir)
    doc_index_path = indexes_dir / "documents.faiss"
    doc_faiss = FAISSManager(dimension=384, index_path=doc_index_path)

    # Code embedder and FAISS index (768-dimensional).
    code_embedder = CodeEmbedder(models_dir)
    code_index_path = indexes_dir / "code.faiss"
    code_faiss = FAISSManager(dimension=768, index_path=code_index_path)

    # Metadata store (shared by both documents and code).
    metadata_store = MetadataStore(db_path)

    # Clear everything if rebuild requested.
    if rebuild:
        logger.info("Rebuild requested - clearing existing indexes and metadata.")
        doc_faiss.reset()
        code_faiss.reset()
        metadata_store.clear_all()

    # Track current FAISS index positions.
    current_doc_faiss_index = doc_faiss.get_count()
    current_code_faiss_index = code_faiss.get_count()

    # Classify and process files.
    classified_counts: dict[str, int] = {
        FileType.CODE.value: 0,
        FileType.DOCUMENT.value: 0,
        FileType.NOTEBOOK.value: 0,
    }
    files_by_type: dict[str, list[str]] = {
        FileType.CODE.value: [],
        FileType.DOCUMENT.value: [],
        FileType.NOTEBOOK.value: [],
    }

    for file_path in files:
        file_type = classify_file(file_path)
        classified_counts[file_type.value] += 1
        files_by_type[file_type.value].append(str(file_path))

        # Process document files.
        if file_type == FileType.DOCUMENT:
            try:
                current_doc_faiss_index = process_document_file(
                    file_path=file_path,
                    metadata_store=metadata_store,
                    doc_embedder=doc_embedder,
                    doc_faiss=doc_faiss,
                    current_doc_faiss_index=current_doc_faiss_index
                )
            except Exception as e:
                # Skip files that fail to process.
                logger.error(f"Failed to process document {file_path}: {e}")
                continue

        # Process code files.
        elif file_type == FileType.CODE:
            try:
                current_code_faiss_index = process_code_file(
                    file_path=file_path,
                    metadata_store=metadata_store,
                    code_embedder=code_embedder,
                    code_faiss=code_faiss,
                    current_code_faiss_index=current_code_faiss_index
                )
            except Exception as e:
                # Skip files that fail to process.
                logger.error(f"Failed to process code file {file_path}: {e}")
                continue

        # Process notebook files.
        elif file_type == FileType.NOTEBOOK:
            try:
                current_doc_faiss_index, current_code_faiss_index = process_notebook_file(
                    file_path=file_path,
                    metadata_store=metadata_store,
                    doc_embedder=doc_embedder,
                    doc_faiss=doc_faiss,
                    code_embedder=code_embedder,
                    code_faiss=code_faiss,
                    current_doc_faiss_index=current_doc_faiss_index,
                    current_code_faiss_index=current_code_faiss_index
                )
            except Exception as e:
                # Skip files that fail to process.
                logger.error(f"Failed to process notebook {file_path}: {e}")
                continue

    logger.info(f"Saving document FAISS index with {doc_faiss.get_count()} vectors.")
    doc_faiss.save()
    logger.info(f"Saving code FAISS index with {code_faiss.get_count()} vectors.")
    code_faiss.save()
    logger.info(f"Indexing complete. Total chunks in metadata: {metadata_store.get_total_chunks()}")

    return IndexResponse(
        total_files=len(files),
        classified=classified_counts,
        files_by_type=files_by_type,
    )


@app.post("/folders", response_model=UpdateFoldersResponse)
def update_folders(request: UpdateFoldersRequest) -> UpdateFoldersResponse:
    """
    Update folders in config.yaml from comma-separated string.

    param request: Request containing comma-separated folder paths.
    """
    logger.info(f"Updating folders configuration: {request.folders}")
    # Parse comma-separated folders.
    folder_list = [folder.strip() for folder in request.folders.split(",")]

    # Load current config from project root.
    project_root = Path(__file__).parent.parent.parent
    config_path = project_root / "config.yaml"
    with open(config_path) as f:
        config_data = yaml.safe_load(f)

    # Update folders in config.
    config_data["indexing"]["folders"] = folder_list

    # Write back to config.yaml.
    with open(config_path, "w") as f:
        yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)

    logger.info(f"Updated folders configuration with {len(folder_list)} folders.")
    return UpdateFoldersResponse(
        message="Folders updated successfully",
        folders=folder_list
    )


@app.post("/search")
def search_documents(request: SearchRequest):
    """
    Search for documents and code using semantic similarity.
    Supports two modes:
    - search: Returns ranked search results
    - answer: Uses LLM to generate answer from search results

    param request: Search request with query, top_k, search_in, and mode.
    """
    logger.info(f"Searching for: {request.query} (mode={request.mode})")

    # Use global search processor (embedders already loaded in memory)
    return search_processor.process_search(request)


@app.get("/health")
def health_check() -> dict[str, str]:
    """
    Health check endpoint.
    """
    return {"status": "ok"}


def start_server() -> None:
    """
    Start the FastAPI development server.
    """
    logger.info("Starting RecallAI server on http://0.0.0.0:8000")
    uvicorn.run(
        "recall_ai.gateway.start_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    start_server()
