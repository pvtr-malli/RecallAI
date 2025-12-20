"""Context builder for RecallAI - builds context from search results."""

from typing import List, Dict, Tuple
from recall_ai.utils.logger import get_logger

logger = get_logger(__name__)


class ContextBuilder:
    """Builds context from search results with deduplication and formatting."""

    def __init__(self, max_context_length: int = 4000):
        """
        Initialize context builder.

        param max_context_length: Maximum total length of context in characters.
        """
        self.max_context_length = max_context_length

    def build_context(
        self,
        search_results: List[Tuple[float, Dict]],
        deduplicate: bool = True
    ) -> Dict:
        """
        Build context from search results.

        param search_results: List of (score, chunk_data) tuples.
        param deduplicate: Whether to deduplicate chunks from same file.
        return: Dictionary with context, sources, and metadata.
        """
        logger.info(f"Building context from {len(search_results)} search results")

        # Step 1: Deduplicate chunks from same files.
        # if deduplicate:
        #     search_results = self._deduplicate_chunks(search_results)
        #     logger.info(f"After deduplication: {len(search_results)} results")

        # Step 2: Format with sources and add file references.
        formatted_chunks = self._format_with_sources(search_results)

        # Step 3: Build final context string (respect max length).
        context_text = self._build_context_text(formatted_chunks)

        # Step 4: Extract unique file references.
        file_references = self._extract_file_references(search_results)

        return {
            "context": context_text,
            "sources": formatted_chunks,
            "file_references": file_references,
            "total_chunks": len(formatted_chunks)
        }

    def _deduplicate_chunks(
        self,
        search_results: List[Tuple[float, Dict]]
    ) -> List[Tuple[float, Dict]]:
        """
        Deduplicate chunks from the same file, keeping best scoring chunk per file.

        param search_results: List of (score, chunk_data) tuples.
        return: Deduplicated list of results.
        """
        seen_files: Dict[str, Tuple[float, Dict]] = {}

        for score, chunk_data in search_results:
            file_path = chunk_data["file_path"]

            # Keep the chunk with the best (lowest) score for each file.
            if file_path not in seen_files or score < seen_files[file_path][0]:
                seen_files[file_path] = (score, chunk_data)

        # Return as list sorted by score.
        deduplicated = list(seen_files.values())
        deduplicated.sort(key=lambda x: x[0])
        return deduplicated

    def _format_with_sources(
        self,
        search_results: List[Tuple[float, Dict]]
    ) -> List[Dict]:
        """
        Format search results with source attribution.

        param search_results: List of (score, chunk_data) tuples.
        return: List of formatted result dictionaries.
        """
        formatted = []

        for idx, (score, chunk_data) in enumerate(search_results, 1):
            formatted.append({
                "index": idx,
                "file_path": chunk_data["file_path"],
                "file_type": chunk_data["file_type"],
                "chunk_text": chunk_data["chunk_text"],
                "chunk_index": chunk_data["chunk_index"],
                "score": score
            })

        return formatted

    def _build_context_text(self, formatted_chunks: List[Dict]) -> str:
        """
        Build context text string from formatted chunks.

        param formatted_chunks: List of formatted chunk dictionaries.
        return: Context text string.
        """
        context_parts = []
        current_length = 0

        for chunk in formatted_chunks:
            # Format: [index] file_path (file_type):\n{chunk_text}\n
            chunk_header = f"[{chunk['index']}] {chunk['file_path']} ({chunk['file_type']}):\n"
            chunk_body = f"{chunk['chunk_text']}\n\n"
            chunk_text = chunk_header + chunk_body

            # Check if adding this chunk exceeds max length.
            if current_length + len(chunk_text) > self.max_context_length:
                logger.info(f"Context length limit reached. Including {len(context_parts)} of {len(formatted_chunks)} chunks.")
                break

            context_parts.append(chunk_text)
            current_length += len(chunk_text)

        return "".join(context_parts)

    def _extract_file_references(
        self,
        search_results: List[Tuple[float, Dict]]
    ) -> List[Dict]:
        """
        Extract unique file references from search results.

        param search_results: List of (score, chunk_data) tuples.
        return: List of unique file reference dictionaries.
        """
        file_refs: Dict[str, Dict] = {}

        for _, chunk_data in search_results:
            file_path = chunk_data["file_path"]
            if file_path not in file_refs:
                file_refs[file_path] = {
                    "file_path": file_path,
                    "file_type": chunk_data["file_type"]
                }

        return list(file_refs.values())
