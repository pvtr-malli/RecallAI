# RecallAI - Indexing Design

## 🏗️ System Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                           RecallAI System                        │
└──────────────────────────────────────────────────────────────────┘

┌──────────────┐      ┌────────────────┐      ┌────────────────┐
│   FastAPI    │◄────►│  Indexer       │◄────►│  Search Engine │
│   Server     │      │  Service       │      │                │
└──────────────┘      └────────────────┘      └────────────────┘
                             │                         │
                             ▼                         ▼
                 ┌────────────────────────────────────────────┐
                 │               Storage Layer                │
                 │                                            │
                 │   ┌──────────────┐    ┌──────────────┐     │
                 │   │ FAISS Index  │    │ FAISS Index  │     │
                 │   │ (Documents)  │    │ (Code)       │     │
                 │   └──────────────┘    └──────────────┘     │
                 │                                            │
                 │            ┌────────────────┐              │
                 │            │ SQLite Metadata│              │
                 │            └────────────────┘              │
                 └────────────────────────────────────────────┘
                             │
                             ▼
                ┌──────────────────────────────────────┐
                │        Embedding Layer               │
                │                                      │
                │  ┌──────────────────────────────┐    │
                │  │ SBERT (Documents / Markdown) │    │
                │  └──────────────────────────────┘    │
                │                                      │
                │  ┌──────────────────────────────┐    │
                │  │ CodeBERT (Code / .py / cells)│    │
                │  └──────────────────────────────┘    │
                └──────────────────────────────────────┘

```

---

## 📥 Indexing Flow
```
User (CLI / UI)
      └──► Indexing API (FastAPI)
               └──► Read Config (Folders)
                        └──► Scan Files
                                 └──► Is Code?
                                          ├──► No (Document)
                                          │        │
                                          │        └──► Doc Embedder (SBERT)
                                          │                 │
                                          │                 └──► FAISS HNSW (Docs)
                                          │
                                          └──► Yes (Code)
                                                   └──► Is .ipynb?
                                                            ├──► No (.py)
                                                            │        │
                                                            │        └──► Code Embedder (CodeBERT)
                                                            │                 │
                                                            │                 └──► FAISS HNSW (Code)
                                                            │
                                                            └──► Yes (.ipynb)
                                                                     ├──► Markdown Cells
                                                                     │        │
                                                                     │        └──► Doc Embedder (SBERT)
                                                                     │                 │
                                                                     │                 └──► FAISS HNSW (Docs)
                                                                     │
                                                                     └──► Code Cells
                                                                              │
                                                                              └──► Code Embedder (CodeBERT)
                                                                                       │
                                                                                       └──► FAISS HNSW (Code)


(All paths → Metadata Indexing ──► Persistent Disk / Volume)
```

```
                          User (CLI / UI)
                                 │
                                 ▼
                      Indexing API (FastAPI)
                                 │
                                 ▼
                      Read Config (Folders)
                                 │
                                 ▼
                           Scan Files
                    (.py .ipynb .md .txt .pdf)
                                 │
                                 ▼
                   Classify: Code or Document?
                                 │
                  ┌──────────────┼──────────────┐
                  │              │              │
                  ▼              ▼              ▼
            Document Flow    Code Flow    Notebook Flow
           (.txt .md .pdf)   (.py files)    (.ipynb)
                  │              │              │
                  │              │              ▼
                  │              │         Split Cells
                  │              │              │
                  │              │         ┌────┴─────┐
                  │              │         │          │
                  │              │         ▼          ▼
                  │              │    Markdown    Code Cells
                  │              │      Cells         │
                  ▼              │         │          │
                  │              │         ▼          │
         Doc Embedder (SBERT) ◄──┼─────────┘          │
                  │              │                    │
                  │              ▼                    ▼
                  │     Code Embedder         Code Embedder
                  │       (CodeBERT)            (CodeBERT)
                  │              │                    │
                  ▼              ▼                    ▼
         FAISS Index (Docs)      │                    │
                  │              │                    │
                  │         FAISS Index (Code) ◄──────┘
                  │              │
                  └──────┬───────┘
                         │
                         ▼
                SQLite Metadata DB
              (file_path, type, hash,
                  chunk_text)
                         │
                         ▼
                  Persist to Disk
                   indexes/ folder

```
## 🔄 Incremental Re-indexing

```
File Change Detection:

  ┌─────────────┐
  │ File System │
  └──────┬──────┘
         │
         ├─► file1.py (modified)
         ├─► file2.md (new)
         └─► file3.txt (deleted)
         │
         ▼
  ┌──────────────────┐
  │ Hash Comparison  │
  └────────┬─────────┘
           │
           ├─► file1.py: hash changed ─► RE-INDEX
           │       │
           │       ├─► Delete old chunks from FAISS
           │       ├─► Delete old metadata from SQLite
           │       └─► Index as new file
           │
           ├─► file2.md: not in DB ─────► INDEX (new)
           │
           └─► file3.txt: in DB but missing ─► DELETE
                   │
                   ├─► Remove chunks from FAISS
                   ├─► DELETE FROM chunks WHERE file_path = ?
                   └─► DELETE FROM files WHERE file_path = ?
```

## 🔍 Query Flow. TODO

```
START: User query "How do I handle errors?"
    │
    ├─► 1. Parse query
    │       │
    │       ├─► Extract filters (if any)
    │       │   Example: "Search in PDF files"
    │       │
    │       └─► Query text: "How do I handle errors?"
    │
    ├─► 2. Generate query embedding
    │       │
    │       ├─► Load embedding model
    │       ├─► Encode query → vector (384 dim)
    │       └─► Output: numpy array
    │
    ├─► 3. Search FAISS index
    │       │
    │       ├─► Similarity search (top k=50)
    │       ├─► Get chunk_ids with scores
    │       └─► Output: [(chunk_id, score), ...]
    │
    ├─► 4. Apply metadata filters (SQLite)
    │       │
    │       ├─► Query: SELECT * FROM chunks
    │       │          WHERE chunk_id IN (...)
    │       │          AND file_type = 'pdf'  -- if filtered
    │       │
    │       └─► Output: List of matching chunks
    │
    ├─► 5. Determine mode
    │       │
    │       ├─────► SEARCH MODE
    │       │       │
    │       │       ├─► Return top N results
    │       │       ├─► Format: file_path + snippet
    │       │       └─► END
    │       │
    │       └─────► ANSWER MODE
    │               │
    │               ├─► Retrieve top chunks as context
    │               ├─► Send to LLM (local model)
    │               ├─► Generate answer
    │               └─► Return: answer + sources
    │
    └─► END: Return results to user
```

---

## 🗄️ Storage Architecture TODO

```
┌────────────────────────────────────────────────────────┐
│                  Storage Layer                         │
└────────────────────────────────────────────────────────┘

┌─────────────────────┐          ┌──────────────────────┐
│  FAISS Index        │          │  SQLite Database     │
│  (embeddings.faiss) │          │  (metadata.db)       │
├─────────────────────┤          ├──────────────────────┤
│                     │          │                      │
│ Chunk 0: [0.2, ...] │◄────────►│ chunks table        │
│ Chunk 1: [0.5, ...] │  sync    │ ├─ chunk_id (PK)   │
│ Chunk 2: [0.1, ...] │          │ ├─ file_path       │
│ ...                 │          │ ├─ file_type       │
│ Chunk N: [0.8, ...] │          │ ├─ chunk_text      │
│                     │          │ └─ chunk_index     │
│ Total: N vectors    │          │                      │
│ Dimension: 384      │          │ files table         │
│                     │          │ ├─ file_path (PK)  │
│                     │          │ ├─ file_hash       │
│                     │          │ ├─ last_indexed    │
│                     │          │ └─ file_size       │
└─────────────────────┘          └──────────────────────┘
         │                                   │
         │                                   │
         └────────── Both persisted ─────────┘
                          │
                          ▼
                   indexes/ folder
```

---



---

## 📊 Data Flow Summary TODO

```
User Files                    Indexing Pipeline              Storage
    │                               │                          │
    ├─ document.pdf ──────┐         │                          │
    ├─ notes.md ──────────┤         │                          │
    ├─ code.py ───────────┼────►  Parse  ──────────────────┐   │
    └─ notebook.ipynb ────┘         │                       │   │
                                    ▼                       │   │
                                  Chunk                     │   │
                                    │                       │   │
                                    ▼                       │   │
                            Generate Embeddings            │   │
                                    │                       │   │
                           ┌────────┴────────┐             │   │
                           ▼                 ▼             │   │
                      FAISS Index      SQLite Metadata     │   │
                           │                 │             │   │
                           └────────┬────────┘             │   │
                                    ▼                      ▼   │
                              Persist to Disk ◄────────────────┘
                                    │
                                    ▼
                         indexes/embeddings.faiss
                         indexes/metadata.db
```

---



---

## 🔐 Consistency Guarantees

```
Transaction Flow:

BEGIN TRANSACTION
    │
    ├─► Add vectors to FAISS (in-memory)
    │
    ├─► INSERT metadata to SQLite
    │
    ├─► Check for errors
    │       │
    │       ├─► ERROR ──► ROLLBACK
    │       │                 │
    │       │                 └─► Discard FAISS changes
    │       │
    │       └─► SUCCESS ──┐
    │                     │
    └─────────────────────┤
                          │
                          ├─► COMMIT SQLite
                          │
                          └─► faiss.write_index()

END TRANSACTION
```

---



## 📏 Metrics & Constraints

```
Embedding Model: all-MiniLM-L6-v2
├─ Dimension: 384
├─ Max sequence: 512 tokens
└─ Size: ~80 MB

Chunk Settings:
├─ Size: 512 tokens (~2000 chars)
├─ Overlap: 50 tokens
└─ Method: Sentence-aware splitting

Estimated Storage:
├─ 1000 files × 10 chunks = 10,000 chunks
├─ FAISS index: 10,000 × 384 × 4 bytes = ~15 MB
└─ SQLite metadata: ~10 MB (with full text)

Total: ~25 MB for 1000 documents
```

## 🚀 Performance Optimizations

1. **Batch Processing**
   - Process multiple files in parallel
   - Batch embed chunks (GPU acceleration if available)

2. **Lazy Loading**
   - Load FAISS index once at startup
   - Keep SQLite connection pooled

3. **Caching**
   - Cache embedding model in memory
   - Cache frequently accessed file metadata

4. **Index Type**
   - Use `IndexFlatL2` for small datasets (<100K vectors)
   - Upgrade to `IndexIVFFlat` for larger datasets
