"""Logging utility for RecallAI."""

import logging
import sys
from pathlib import Path


def setup_logger(name: str = "recallai", level: int = logging.INFO) -> logging.Logger:
    """
    Set up logger with console and file handlers.

    param name: Logger name.
    param level: Logging level.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding duplicate handlers.
    if logger.handlers:
        return logger

    # Console handler.
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler - use project root for logs.
    # Find project root by looking for pyproject.toml.
    current_path = Path(__file__).resolve()
    project_root = current_path
    while project_root.parent != project_root:
        if (project_root / "pyproject.toml").exists():
            break
        project_root = project_root.parent
    else:
        # Fallback to cwd if pyproject.toml not found.
        project_root = Path.cwd()

    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "recallai.log")
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "recallai") -> logging.Logger:
    """
    Get existing logger or create new one.

    param name: Logger name.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger
