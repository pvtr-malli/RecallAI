"""File scanner for RecallAI."""
from enum import Enum
from pathlib import Path
from recall_ai.utils.config import IndexConfig
from recall_ai.utils.logger import get_logger

logger = get_logger(__name__)


def scan_files(config: IndexConfig) -> list[Path]:
    """
    Scan folders for files matching supported extensions.

    param config: Index configuration with folders and extensions.
    """
    logger.info(f"Starting file scan for {len(config.folders)} folders.")
    files: list[Path] = []
    extensions_set: set[str] = set(config.supported_extensions)
    exclude_set: set[str] = set(config.exclude)

    for folder in config.folders:
        if not folder.exists():
            logger.warning(f"Folder does not exist: {folder}")
            continue

        logger.info(f"Scanning folder: {folder}")
        # Recursively find all files.
        for file_path in folder.rglob("*"):
            # Skip directories.
            if not file_path.is_file():
                continue

            # Skip excluded patterns.
            if any(pattern in file_path.parts for pattern in exclude_set):
                continue

            # Check if extension is supported.
            if file_path.suffix in extensions_set:
                files.append(file_path)

    logger.info(f"Scan complete. Found {len(files)} files.")
    return files


class FileType(Enum):
    """
    File type classification.
    """

    CODE: str = "code"
    DOCUMENT: str = "document"
    NOTEBOOK: str = "notebook"


def classify_file(file_path: Path) -> FileType:
    """
    Classify file as code, document, or notebook.

    param file_path: Path to the file to classify.
    """
    extension = file_path.suffix.lower()

    if extension == ".ipynb":
        file_type = FileType.NOTEBOOK
    elif extension == ".py":
        file_type = FileType.CODE
    else:
        # .txt, .md, .pdf are documents.
        file_type = FileType.DOCUMENT

    logger.debug(f"Classified {file_path.name} as {file_type.value}.")
    return file_type
