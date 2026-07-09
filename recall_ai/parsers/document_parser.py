"""Document parser for RecallAI."""

from pathlib import Path
from pypdf import PdfReader
from recall_ai.utils.logger import get_logger

logger = get_logger(__name__)


def parse_document(file_path: Path) -> str:
    """
    Parse document file and extract text content.

    param file_path: Path to the document file.
    """
    logger.debug(f"Parsing document: {file_path}")
    extension = file_path.suffix.lower()

    if extension == ".txt":
        return _parse_txt(file_path)
    elif extension == ".md":
        return _parse_md(file_path)
    elif extension == ".pdf":
        return _parse_pdf(file_path)
    else:
        logger.error(f"Unsupported document type: {extension}")
        raise ValueError(f"Unsupported document type: {extension}")


def _parse_txt(file_path: Path) -> str:
    """
    Parse .txt file.

    param file_path: Path to the text file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def _parse_md(file_path: Path) -> str:
    """
    Parse .md file.

    param file_path: Path to the markdown file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def _parse_pdf(file_path: Path) -> str:
    """
    Parse .pdf file.

    param file_path: Path to the PDF file.
    """
    from pypdf.errors import PdfReadError

    try:
        reader = PdfReader(file_path)
    except PdfReadError as e:
        logger.error(f"Failed to read PDF {file_path.name}: {e}")
        raise ValueError(f"Invalid or corrupted PDF file: {file_path.name}") from e
    except Exception as e:
        logger.error(f"Unexpected error reading PDF {file_path.name}: {e}")
        raise

    text_parts: list[str] = []

    for page_num, page in enumerate(reader.pages):
        try:
            text = page.extract_text()
            if text.strip():
                text_parts.append(text)
        except (PdfReadError, KeyError, ValueError) as e:
            logger.warning(f"Failed to extract text from page {page_num} of {file_path.name}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error on page {page_num} of {file_path.name}: {e}")
            continue

    if not text_parts:
        logger.warning(f"No text extracted from PDF {file_path.name}")
        return ""

    return "\n\n".join(text_parts)
