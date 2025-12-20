"""Pydantic models for RecallAI API requests and responses."""

from pydantic import BaseModel


class UpdateFoldersRequest(BaseModel):
    """
    Request to update indexed folders.
    """

    folders: str


class UpdateFoldersResponse(BaseModel):
    """
    Response from updating folders.
    """

    message: str
    folders: list[str]


class IndexResponse(BaseModel):
    """
    Response from indexing operation.
    """

    total_files: int
    classified: dict[str, int]
    files_by_type: dict[str, list[str]]


class SearchRequest(BaseModel):
    """
    Request to search for documents.
    """

    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    """
    Single search result.
    """

    chunk_text: str
    file_path: str
    file_type: str
    chunk_index: int
    score: float


class SearchResponse(BaseModel):
    """
    Response from search operation.
    """

    query: str
    results: list[SearchResult]
