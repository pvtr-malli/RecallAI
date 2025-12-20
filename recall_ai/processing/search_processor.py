"""Search processor for RecallAI - handles search and answer generation."""

from pathlib import Path
from typing import Union, List, Tuple, Dict

from recall_ai.embeddings.document_embedder import DocumentEmbedder
from recall_ai.embeddings.code_embedder import CodeEmbedder
from recall_ai.embeddings.faiss_manager import FAISSManager
from recall_ai.embeddings.metadata_store import MetadataStore
from recall_ai.processing.context_builder import ContextBuilder
from recall_ai.processing.llm_client import LLMClient
from recall_ai.gateway.models import SearchRequest, SearchResult, SearchResponse, AnswerResponse
from recall_ai.utils.logger import get_logger

logger = get_logger(__name__)


class SearchProcessor:
    """Processes search requests in both search and answer modes."""

    def __init__(
        self,
        models_dir: Path,
        indexes_dir: Path,
        db_path: Path
    ):
        """
        Initialize search processor.

        param models_dir: Directory containing embedding models.
        param indexes_dir: Directory containing FAISS indexes.
        param db_path: Path to SQLite metadata database.
        """
        self.models_dir = models_dir
        self.indexes_dir = indexes_dir
        self.db_path = db_path

        # Initialize embedders, FAISS indexes, and metadata store.
        logger.info("Initializing search processor components")
        self.doc_embedder = DocumentEmbedder(models_dir)
        self.doc_index_path = indexes_dir / "documents.faiss"
        self.doc_faiss = FAISSManager(dimension=384, index_path=self.doc_index_path)

        self.code_embedder = CodeEmbedder(models_dir)
        self.code_index_path = indexes_dir / "code.faiss"
        self.code_faiss = FAISSManager(dimension=768, index_path=self.code_index_path)

        self.metadata_store = MetadataStore(db_path)

    def process_search(
        self,
        request: SearchRequest
    ) -> Union[SearchResponse, AnswerResponse]:
        """
        Process search request in either search or answer mode.

        param request: Search request with query, top_k, search_in, and mode.
        return: SearchResponse or AnswerResponse depending on mode.
        """
        logger.info(f"Processing search: {request.query} (mode={request.mode})")

        # Validate parameters.
        if request.search_in not in ("documents", "code", "both"):
            logger.warning(f"Invalid search_in value: {request.search_in}, defaulting to 'both'")
            request.search_in = "both"

        if request.mode not in ("search", "answer"):
            logger.warning(f"Invalid mode value: {request.mode}, defaulting to 'search'")
            request.mode = "search"

        # Perform semantic search across indexes.
        search_results = self._search_indexes(request)
        logger.info(f"Found {len(search_results)} results for query: {request.query}")

        # Route to appropriate mode handler.
        if request.mode == "search":
            return self._handle_search_mode(request.query, search_results)
        else:
            return self._handle_answer_mode(request.query, search_results)

    def _search_indexes(
        self,
        request: SearchRequest
    ) -> List[Tuple[float, Dict]]:
        """
        Search FAISS indexes based on request parameters.

        param request: Search request with query, top_k, and search_in.
        return: List of (score, chunk_data) tuples sorted by score.
        """
        all_results: List[Tuple[float, Dict]] = []

        # Search document index if requested.
        if request.search_in in ("documents", "both") and self.doc_faiss.get_count() > 0:
            doc_query_embedding = self.doc_embedder.embed_single(request.query)
            doc_distances, doc_indices = self.doc_faiss.search(doc_query_embedding, k=request.top_k)
            for distance, faiss_idx in zip(doc_distances, doc_indices):
                chunk_data = self.metadata_store.get_chunk_by_faiss_index(int(faiss_idx))
                if chunk_data:
                    all_results.append((float(distance), chunk_data))

        # Search code index if requested.
        if request.search_in in ("code", "both") and self.code_faiss.get_count() > 0:
            code_query_embedding = self.code_embedder.embed_single(request.query)
            code_distances, code_indices = self.code_faiss.search(code_query_embedding, k=request.top_k)
            for distance, faiss_idx in zip(code_distances, code_indices):
                chunk_data = self.metadata_store.get_chunk_by_faiss_index(int(faiss_idx))
                if chunk_data:
                    all_results.append((float(distance), chunk_data))

        # Sort combined results by score (distance) and take top_k.
        all_results.sort(key=lambda x: x[0])
        return all_results[:request.top_k]

    def _handle_search_mode(
        self,
        query: str,
        search_results: List[Tuple[float, Dict]]
    ) -> SearchResponse:
        """
        Handle search mode - return file metadata.

        param query: User's query.
        param search_results: List of (score, chunk_data) tuples.
        return: SearchResponse with ranked results.
        """
        results: List[SearchResult] = []
        for score, chunk_data in search_results:
            results.append(SearchResult(
                chunk_text=chunk_data["chunk_text"],
                file_path=chunk_data["file_path"],
                file_type=chunk_data["file_type"],
                chunk_index=chunk_data["chunk_index"],
                score=score
            ))
        return SearchResponse(query=query, results=results)

    def _handle_answer_mode(
        self,
        query: str,
        search_results: List[Tuple[float, Dict]]
    ) -> Union[AnswerResponse, SearchResponse]:
        """
        Handle answer mode - build context and generate answer with LLM.

        param query: User's query.
        param search_results: List of (score, chunk_data) tuples.
        return: AnswerResponse with answer and sources, or SearchResponse if LLM fails.
        """
        # Build context from search results.
        context_builder = ContextBuilder(max_context_length=4000)
        context_data = context_builder.build_context(search_results, deduplicate=True)

        # Initialize LLM client (uses Llama 3.1 8B Instruct by default).
        llm_client = LLMClient()

        try:
            # Generate answer using LLM.
            answer = llm_client.generate_answer(
                query=query,
                context=context_data["context"]
            )

            # Convert sources to SearchResult objects.
            source_results: List[SearchResult] = []
            for source in context_data["sources"]:
                source_results.append(SearchResult(
                    chunk_text=source["chunk_text"],
                    file_path=source["file_path"],
                    file_type=source["file_type"],
                    chunk_index=source["chunk_index"],
                    score=source["score"]
                ))

            logger.info(f"Generated answer for query: {query}")
            return AnswerResponse(
                query=query,
                answer=answer,
                sources=source_results,
                file_references=context_data["file_references"]
            )

        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            # Fallback to search mode if LLM fails.
            return self._handle_search_mode(query, search_results)
