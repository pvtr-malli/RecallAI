"""Configuration management for RecallAI."""

from pathlib import Path
from pydantic import BaseModel, Field, field_validator
import yaml


class IndexConfig(BaseModel):
    """
    Configuration for indexing.
    """

    folders: list[Path] = Field(description="List of folders to scan for files.")
    exclude: list[str] = Field(
        default=["__pycache__", ".venv", "venv", "node_modules", ".git"],
        description="Folder patterns to exclude from scanning."
    )
    supported_extensions: list[str] = Field(
        default=[".py", ".ipynb", ".md", ".txt", ".pdf"],
        description="File extensions to index."
    )

    @field_validator("folders", mode="before")
    @classmethod
    def expand_paths(cls, v: list[str]) -> list[Path]:
        """
        Expand home directory in folder paths.

        param v: List of folder path strings.
        """
        return [Path(folder).expanduser() for folder in v]


class RecallAIConfig(BaseModel):
    """
    Main configuration for RecallAI.
    """

    indexing: IndexConfig
    models_dir: Path = Field(
        default=Path("models"),
        description="Directory where embedding models are stored."
    )
    indexes_dir: Path = Field(
        default=Path("indexes"),
        description="Directory where FAISS indexes are stored."
    )
    db_path: Path = Field(
        default=Path("indexes/metadata.db"),
        description="Path to SQLite metadata database."
    )


def load_config(config_path: Path = Path("config.yaml")) -> RecallAIConfig:
    """
    Load configuration from YAML file.

    param config_path: Path to the configuration YAML file.
    """
    with open(config_path) as f:
        config_data = yaml.safe_load(f)
    return RecallAIConfig(**config_data)
