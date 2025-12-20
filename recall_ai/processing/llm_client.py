"""LLM client for RecallAI - uses Ollama with Llama 3.1 8B Instruct."""

from typing import Optional
import requests
from recall_ai.utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    """Client for interacting with Ollama LLM."""

    def __init__(
        self,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize LLM client with Ollama.

        param model: Model name (defaults to llama3.1:8b-instruct-q4_0).
        param base_url: Base URL for Ollama API (defaults to http://localhost:11434).
        """
        self.provider = "ollama"
        self.base_url = base_url if base_url else "http://localhost:11434"
        self.model = model if model else "llama3.1:8b-instruct-q4_0"

        logger.info(f"Initialized LLM client: provider={self.provider}, model={self.model}")

    def generate_answer(self, query: str, context: str) -> str:
        """
        Generate answer using Ollama.

        param query: User's query.
        param context: Context built from search results.
        return: Generated answer.
        """
        logger.info(f"Generating answer for query: {query[:100]}...")

        # Build prompt.
        prompt = self._build_prompt(query, context)

        # Call Ollama.
        return self._call_ollama(prompt)

    def _build_prompt(self, query: str, context: str) -> str:
        """
        Build prompt for LLM with context and query.

        param query: User's query.
        param context: Context from search results.
        return: Formatted prompt.
        """
        prompt = f"""You are a helpful assistant that answers questions ONLY based on the provided context.

Context from relevant documents and code:
{context}

User question: {query}

Please provide a clear and accurate answer based on the context above. If the context doesn't contain enough information to answer the question, say so.

Answer:"""
        return prompt

    def _call_ollama(self, prompt: str) -> str:
        """
        Call Ollama API.

        param prompt: Formatted prompt.
        return: Generated answer.
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API error: {e}")
            raise RuntimeError(f"Failed to call Ollama API: {e}")
