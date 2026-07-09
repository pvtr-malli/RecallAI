"""Metadata storage for RecallAI using SQLite."""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional
from recall_ai.utils.logger import get_logger

logger = get_logger(__name__)


class MetadataStore:
    """
    SQLite-based metadata storage for chunks and files.
    """

    def __init__(self, db_path: Path) -> None:
        """
        Initialize metadata store.

        param db_path: Path to SQLite database file.
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info(f"Metadata store initialized at {db_path}")

    def _init_db(self) -> None:
        """
        Initialize database schema.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Files table.
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_type TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    last_modified REAL NOT NULL,
                    indexed_at REAL NOT NULL
                )
            """)

            # Chunks table.
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    chunk_text TEXT NOT NULL,
                    faiss_index INTEGER NOT NULL,
                    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
                )
            """)

            # Create indexes for faster lookups.
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunks_faiss
                ON chunks(faiss_index)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunks_file
                ON chunks(file_id)
            """)

            conn.commit()
            logger.debug("Database schema initialized.")

    def add_file(
        self,
        file_path: str,
        file_type: str,
        file_hash: str,
        last_modified: float
    ) -> int:
        """
        Add or update file metadata.

        param file_path: Path to the file.
        param file_type: Type of file (code, document, notebook).
        param file_hash: Hash of file content.
        param last_modified: File modification timestamp.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO files
                (file_path, file_type, file_hash, last_modified, indexed_at)
                VALUES (?, ?, ?, ?, ?)
            """, (file_path, file_type, file_hash, last_modified, datetime.now().timestamp()))

            file_id = cursor.lastrowid
            conn.commit()
            logger.debug(f"Added file metadata: {file_path} (id={file_id})")
            return file_id

    def add_chunk(
        self,
        file_id: int,
        chunk_index: int,
        chunk_text: str,
        faiss_index: int
    ) -> int:
        """
        Add chunk metadata.

        param file_id: ID of the parent file.
        param chunk_index: Index of chunk within the file.
        param chunk_text: Text content of the chunk.
        param faiss_index: Index in FAISS vector store.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chunks
                (file_id, chunk_index, chunk_text, faiss_index)
                VALUES (?, ?, ?, ?)
            """, (file_id, chunk_index, chunk_text, faiss_index))

            chunk_id = cursor.lastrowid
            conn.commit()
            logger.debug(f"Added chunk metadata: file_id={file_id}, faiss_index={faiss_index}")
            return chunk_id

    def get_chunk_by_faiss_index(self, faiss_index: int) -> Optional[dict]:
        """
        Get chunk and file metadata by FAISS index.

        param faiss_index: Index in FAISS vector store.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    c.id as chunk_id,
                    c.chunk_text,
                    c.chunk_index,
                    f.file_path,
                    f.file_type,
                    f.last_modified
                FROM chunks c
                JOIN files f ON c.file_id = f.id
                WHERE c.faiss_index = ?
            """, (faiss_index,))

            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def get_file_by_path(self, file_path: str) -> Optional[dict]:
        """
        Get file metadata by path.

        param file_path: Path to the file.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM files WHERE file_path = ?
            """, (file_path,))

            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def delete_file(self, file_path: str) -> None:
        """
        Delete file and its chunks.

        param file_path: Path to the file.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM files WHERE file_path = ?
            """, (file_path,))
            conn.commit()
            logger.debug(f"Deleted file metadata: {file_path}")

    def clear_all(self) -> None:
        """
        Clear all metadata.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chunks")
            cursor.execute("DELETE FROM files")
            conn.commit()
            logger.info("Cleared all metadata.")

    def get_total_chunks(self) -> int:
        """
        Get total number of chunks.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM chunks")
            return cursor.fetchone()[0]

    def get_total_files(self) -> int:
        """
        Get total number of files.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM files")
            return cursor.fetchone()[0]
