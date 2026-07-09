"""Notebook parser for RecallAI."""

import json
from pathlib import Path
from typing import Literal
from recall_ai.utils.logger import get_logger

logger = get_logger(__name__)

CellType = Literal["markdown", "code"]


class NotebookCell:
    """Represents a single cell from a Jupyter notebook."""

    def __init__(self, cell_type: CellType, content: str, cell_index: int) -> None:
        """
        Initialize notebook cell.

        param cell_type: Type of cell (markdown or code).
        param content: Cell content as string.
        param cell_index: Index of cell in notebook.
        """
        self.cell_type = cell_type
        self.content = content
        self.cell_index = cell_index


def parse_notebook(file_path: Path) -> list[NotebookCell]:
    """
    Parse Jupyter notebook and extract cells.

    param file_path: Path to the .ipynb file.
    return: List of NotebookCell objects.
    """
    logger.debug(f"Parsing notebook: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            notebook_data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse notebook JSON {file_path.name}: {e}")
        raise ValueError(f"Invalid notebook JSON: {file_path.name}") from e
    except UnicodeDecodeError as e:
        logger.error(f"Failed to decode notebook {file_path.name}: {e}")
        raise ValueError(f"Invalid encoding in notebook: {file_path.name}") from e
    except Exception as e:
        logger.error(f"Unexpected error reading notebook {file_path.name}: {e}")
        raise

    if "cells" not in notebook_data:
        logger.warning(f"No cells found in notebook {file_path.name}")
        return []

    cells: list[NotebookCell] = []
    for idx, cell in enumerate(notebook_data["cells"]):
        cell_type = cell.get("cell_type")

        # Only process markdown and code cells.
        if cell_type not in ("markdown", "code"):
            logger.debug(f"Skipping cell type '{cell_type}' in {file_path.name}")
            continue

        # Extract source content.
        source = cell.get("source", [])
        if isinstance(source, list):
            content = "".join(source)
        elif isinstance(source, str):
            content = source
        else:
            logger.warning(f"Unexpected source type in cell {idx} of {file_path.name}")
            continue

        # Skip empty cells.
        if not content.strip():
            continue

        cells.append(NotebookCell(
            cell_type=cell_type,  # type: ignore
            content=content,
            cell_index=idx
        ))

    logger.info(f"Extracted {len(cells)} cells from {file_path.name}")
    return cells
