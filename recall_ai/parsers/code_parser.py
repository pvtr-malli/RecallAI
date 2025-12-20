"""Code parser for RecallAI."""

from pathlib import Path
from recall_ai.utils.logger import get_logger

logger = get_logger(__name__)


def parse_code(file_path: Path) -> str:
    """
    Parse code file and extract text content.

    param file_path: Path to the code file.
    """
    logger.debug(f"Parsing code file: {file_path}")
    extension = file_path.suffix.lower()

    if extension == ".py":
        return _parse_python(file_path)
    else:
        logger.error(f"Unsupported code file type: {extension}")
        raise ValueError(f"Unsupported code file type: {extension}")


def _parse_python(file_path: Path) -> str:
    """
    Parse .py file.

    param file_path: Path to the Python file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError as e:
        logger.error(f"Failed to decode Python file {file_path.name}: {e}")
        raise ValueError(f"Invalid encoding in Python file: {file_path.name}") from e
    except Exception as e:
        logger.error(f"Unexpected error reading Python file {file_path.name}: {e}")
        raise
