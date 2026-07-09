"""Text chunking for RecallAI using LangChain."""
from recall_ai.utils.logger import get_logger
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownTextSplitter


logger = get_logger(__name__)

def chunk_text(text: str, file_extension: str = ".txt", chunk_size: int = 512, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks using document-aware splitting.

    param text: Text content to chunk.
    param file_extension: File extension to determine splitter type.
    param chunk_size: Maximum number of tokens per chunk.
    param overlap: Number of overlapping tokens between chunks.
    """
    # Approximate character count (1 token ≈ 4 chars).
    char_chunk_size = chunk_size * 4
    char_overlap = overlap * 4

    # Use markdown-aware splitter for .md files.
    if file_extension == ".md":
        splitter = MarkdownTextSplitter(
            chunk_size=char_chunk_size,
            chunk_overlap=char_overlap
        )
    else:
        # Use recursive splitter for other text files.
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=char_chunk_size,
            chunk_overlap=char_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    chunks = splitter.split_text(text)
    return [c for c in chunks if c.strip()]  # Filter empty chunks.


def chunk_code(code: str, language: str = "python", chunk_size: int = 512, overlap: int = 50) -> list[str]:
    """
    Split code into overlapping chunks using language-aware splitting.

    param code: Code content to chunk.
    param language: Programming language (python, etc.).
    param chunk_size: Maximum number of tokens per chunk.
    param overlap: Number of overlapping tokens between chunks.
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    # Approximate character count.
    char_chunk_size = chunk_size * 4
    char_overlap = overlap * 4

    # Python-specific separators (respects function/class boundaries).
    if language == "python":
        separators = ["\nclass ", "\ndef ", "\n\n", "\n", " ", ""]
    else:
        separators = ["\n\n", "\n", " ", ""]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=char_chunk_size,
        chunk_overlap=char_overlap,
        separators=separators
    )

    chunks = splitter.split_text(code)
    return [c for c in chunks if c.strip()]
