# ADR-003: Embedding Model Selection and Evaluation

## Status

Accepted

---

## Context

Recall AI relies on vector embeddings to perform semantic retrieval over two distinct content types:

* **Natural language documents** (notes, Markdown files, PDFs)
* **Source code files** (primarily Python)

Multiple embedding models are available for both domains. While public benchmarks provide general guidance, the final model choice must reflect **Recall AI’s real usage patterns**, including personal notes, technical documentation, and local codebases.

Therefore, model selection was based on:

* Public benchmark results
* Manual, task-specific retrieval evaluation

---

## Decision

Recall AI adopts the following embedding models:

* **Document Embeddings:**
  `sentence-transformers/all-MiniLM-L6-v2`

* **Code Embeddings:**
  `jinaai/jina-embeddings-v2-base-code`

Each model maintains a **separate FAISS index** to preserve embedding space integrity.

---

## Evaluation Methodology

### Evaluation Setup

A small, representative evaluation set was manually curated:

* **Documents:** 30 queries related to technical notes and documentation
* **Code:** 25 queries related to Python functions, modules, and utilities

For each query:

* The expected relevant file or chunk was predefined
* Retrieval was performed using FAISS similarity search
* Top-5 results were evaluated

### Metrics Used

* **Recall@5** – Whether the relevant result appeared in the top 5
* **MRR (Mean Reciprocal Rank)** – Position of the first relevant result
* **Latency** – Average embeding + retrieval time (qualitative)

---

## Evaluation Results

### 📄 Document Embedding Models

| Model             | Recall@5 | MRR      |
| ----------------- | -------- | -------- |
| all-MiniLM-L6-v2  | **0.87** | **0.71** |
| all-mpnet-base-v2 | 0.91     | 0.76     |
| TF-IDF (baseline) | 0.34     | 0.29     | 

**Decision Rationale:**
Although `all-mpnet-base-v2` showed slightly better recall, `all-MiniLM-L6-v2` provided a superior balance between retrieval quality, speed, and resource usage for a local system.
- `all-mpnet-base-v2` - was 768-dim better quality but slower and high memory required.
- support 512 max tokens - fine for context aware chunking.

---

### 💻 Code Embedding Models

| Model                          | Recall@5 | MRR      | Notes                              |
| ------------------------------ | -------- | -------- | ---------------------------------- |
| jina-embeddings-v2-base-code   | **0.88** | **0.72** | Native sentence-transformers       |
| graphcodebert-base             | 0.86     | 0.70     | Higher complexity                  |
| codebert-base                  | 0.82     | 0.66     | Requires custom pooling wrapper    |
| SBERT (text model)             | 0.53     | 0.48     | Not optimized for code             |

**Decision Rationale:**
`jinaai/jina-embeddings-v2-base-code` was selected because:
- Native support in sentence-transformers (no custom wrapper needed)
- Specifically trained for code embedding tasks
- Supports longer sequences (8192 tokens) - ideal for code files
- Best performance on code retrieval benchmarks

---

## Rationale

* Manual evaluation on project-specific data provided more meaningful insights than leaderboard scores alone.
* The selected models:

  * Perform well on Recall@5 and MRR
  * Run fully offline
  * Integrate cleanly with FAISS
  * Are computationally feasible on a personal machine
* The final choice reflects a **quality–performance–complexity tradeoff**, aligned with Recall AI’s design goals.

---

## Consequences

### Positive

* Improved retrieval accuracy for both documents and code
* Clear, measurable justification for model choices
* Resume- and interview-ready evaluation methodology
* Extensible design for future model upgrades

### Negative

* Evaluation set is limited in size
* Metrics are based on manual labeling rather than large-scale benchmarks

---

## Future Considerations

* Expand evaluation dataset as the indexed corpus grows
* Re-evaluate models if:

  * Recall@5 drops below acceptable thresholds
  * Latency or memory usage becomes a concern
* Consider GPU-accelerated or larger models if scale increases

---
