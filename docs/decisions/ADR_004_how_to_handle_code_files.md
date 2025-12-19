# ADR-006: Code and Notebook Ingestion Strategy

## Status

Accepted

---

## Context

Recall AI indexes a mixed set of files that include:

* Standalone source code files (e.g., `.py`)
* Jupyter notebooks (`.ipynb`) containing both:

  * Markdown (natural language explanations)
  * Code cells (executable source code)

Recall AI uses **separate embedding models and FAISS indexes** for:

* Natural language documents
* Source code

Therefore, a clear and consistent ingestion strategy is required to ensure:

* Correct embedding model selection
* Proper isolation of embedding spaces
* High-quality semantic retrieval for both documentation and code

---

## Decision

Recall AI will apply **content-type–aware ingestion rules** during indexing:

1. **`.py` files**

   * Entire file content is treated as source code
   * Embedded exclusively using the **code embedding model**
   * Indexed only in the **code FAISS index**

2. **`.ipynb` files**

   * Parsed at the cell level
   * Markdown cells are treated as natural language text
   * Code cells are treated as source code
   * Markdown cells are embedded using the **document embedding model** and indexed in the **document FAISS index**
   * Code cells are embedded using the **code embedding model** and indexed in the **code FAISS index**

This approach ensures that each piece of content is embedded using the model best suited to its semantic structure.

---

## Rationale

* Standalone `.py` files consist entirely of source code and benefit from code-specific embeddings that capture programming-related semantics.
* Jupyter notebooks are **hybrid artifacts** that mix:

  * Explanatory text (Markdown)
  * Executable code
* Treating notebook content uniformly would reduce retrieval quality.
* Cell-level separation allows:

  * Markdown explanations to be retrieved through natural language queries
  * Code logic to be retrieved through code-focused queries
* This strategy aligns with Recall AI’s dual-embedding architecture and avoids mixing incompatible embedding spaces.

---

## Implementation Notes

* `.ipynb` files will be parsed as JSON
* Each cell will generate one or more chunks depending on size
* Metadata stored per chunk will include:

  * File path
  * Cell type (`markdown` or `code`)
  * Cell index
* Chunking rules may differ for code and text cells
* Embedding and indexing steps must enforce strict separation between document and code indexes

---
