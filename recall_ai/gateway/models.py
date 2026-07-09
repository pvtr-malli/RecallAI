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
    search_in: str = "both"  # Options: "documents", "code", "both"
    mode: str = "search"  # Options: "search", "answer"


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


class AnswerResponse(BaseModel):
    """
    Response from answer operation (with LLM).
    """

    query: str
    answer: str
    sources: list[SearchResult]
    file_references: list[dict[str, str]]
