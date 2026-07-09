# RecallAI API Documentation

RecallAI provides a RESTful API for indexing and searching your local documents and code files using semantic search and LLM-powered answers.

## Base URL

```
http://localhost:8000
```

---

## Endpoints

### 1. Health Check

Check if the server is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "ok"
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

### 2. Update Folders

Update the folders to be indexed in the configuration.

**Endpoint:** `POST /folders`

**Request Body:**
```json
{
  "folders": "~/projects/notes, ~/documents, ~/code"
}
```

**Parameters:**
- `folders` (string, required): Comma-separated list of folder paths to index

**Response:**
```json
{
  "message": "Folders updated successfully",
  "folders": [
    "~/projects/notes",
    "~/documents",
    "~/code"
  ]
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/folders \
  -H "Content-Type: application/json" \
  -d '{"folders": "~/projects/notes, ~/documents"}'
```

---

### 3. Index Files

Index all files from configured folders. This processes documents, code files, and notebooks, creating embeddings and storing them in FAISS indexes.

**Endpoint:** `POST /index`

**Query Parameters:**
- `rebuild` (boolean, optional): If `true`, clears existing index and rebuilds from scratch. Default: `false`

**Response:**
```json
{
  "total_files": 150,
  "classified": {
    "code": 75,
    "document": 60,
    "notebook": 15
  },
  "files_by_type": {
    "code": [
      "/path/to/file1.py",
      "/path/to/file2.js"
    ],
    "document": [
      "/path/to/doc1.md",
      "/path/to/doc2.txt"
    ],
    "notebook": [
      "/path/to/notebook1.ipynb"
    ]
  }
}
```

**Example:**
```bash
# Index new/modified files
curl -X POST http://localhost:8000/index

# Rebuild entire index from scratch
curl -X POST "http://localhost:8000/index?rebuild=true"
```

---

### 4. Search

Search for documents and code using semantic similarity. Supports two modes: search (returns ranked results) and answer (generates LLM-powered answers).

**Endpoint:** `POST /search`

**Request Body:**
```json
{
  "query": "How to handle authentication?",
  "top_k": 5,
  "search_in": "both",
  "mode": "answer"
}
```

**Parameters:**
- `query` (string, required): The search query
- `top_k` (integer, optional): Number of results to return. Default: `5`
- `search_in` (string, optional): Where to search. Options: `"documents"`, `"code"`, `"both"`. Default: `"both"`
- `mode` (string, optional): Search mode. Options: `"search"`, `"answer"`. Default: `"search"`

#### Mode: Search

Returns ranked search results based on semantic similarity.

**Response:**
```json
{
  "query": "How to handle authentication?",
  "results": [
    {
      "chunk_text": "Authentication is handled using JWT tokens...",
      "file_path": "/path/to/auth.py",
      "file_type": "code",
      "chunk_index": 0,
      "score": 0.234
    },
    {
      "chunk_text": "To implement authentication, follow these steps...",
      "file_path": "/path/to/auth-guide.md",
      "file_type": "document",
      "chunk_index": 2,
      "score": 0.456
    }
  ]
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to handle authentication?",
    "top_k": 5,
    "search_in": "both",
    "mode": "search"
  }'
```

#### Mode: Answer

Uses LLM to generate natural language answers based on the retrieved context.

**Response:**
```json
{
  "query": "How to handle authentication?",
  "answer": "Based on the provided context, authentication is handled using JWT tokens. The auth.py module implements token generation and validation. To implement authentication, you need to: 1) Set up the authentication middleware, 2) Create login endpoints, 3) Validate tokens on protected routes.",
  "sources": [
    {
      "chunk_text": "Authentication is handled using JWT tokens...",
      "file_path": "/path/to/auth.py",
      "file_type": "code",
      "chunk_index": 0,
      "score": 0.234
    },
    {
      "chunk_text": "To implement authentication, follow these steps...",
      "file_path": "/path/to/auth-guide.md",
      "file_type": "document",
      "chunk_index": 2,
      "score": 0.456
    }
  ],
  "file_references": [
    {
      "file_path": "/path/to/auth.py",
      "file_type": "code"
    },
    {
      "file_path": "/path/to/auth-guide.md",
      "file_type": "document"
    }
  ]
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to handle authentication?",
    "top_k": 5,
    "search_in": "both",
    "mode": "answer"
  }'
```

---


## Performance Notes

1. **First Search After Startup**: The first search request loads embedding models into memory (takes 10-20 seconds). Subsequent requests are much faster.

2. **LLM Answer Generation**: Answer mode takes longer than search mode (5-15 seconds) because it calls the LLM to generate natural language answers.

3. **Indexing**: Initial indexing can take time depending on the number of files. Use rebuild sparingly.

4. **Search Speed**: Once models are loaded, search mode typically returns results in under 1 second.

---

The server runs on `http://localhost:8000` by default with auto-reload enabled for development.
