# ADR-002: Embedding Model and Strategy

## Status

Accepted

---

## Context

Recall AI performs semantic search over a **mixed corpus** consisting of:

* Natural language documents (notes, Markdown files, PDFs)
* Source code files (primarily Python: `.py`, `.ipynb`)

These two content types differ significantly in structure and semantics.
Natural language focuses on meaning and context, while source code relies on identifiers, syntax, and structural patterns.

The embedding strategy must satisfy the following constraints:

* Fully local and offline operation
* Compatibility with FAISS
* High-quality semantic retrieval for both documents and code
* Persistence across restarts
* Manageable system complexity suitable for a single-user system
* Clear extensibility for future improvements

---

## Decision

Recall AI will use **two separate embedding models**:

* A **general-purpose SBERT-based model** for natural language documents
* A **code-specific embedding model** for source code files

Each embedding model will maintain its **own FAISS index**, ensuring that vectors from different embedding spaces are never mixed.

---

## Alternatives Considered

### 1. Single Embedding Model for All Content

* Use a single SBERT-based model for documents and code
* Maintain one FAISS index

### 2. Hybrid Retrieval with Merged Results

* Embed queries using both models
* Search both indexes
* Merge and re-rank results

---

## Rationale

* Code and natural language exhibit **fundamentally different semantic structures**, and no single embedding model performs optimally for both.
* Code-specific embedding models better capture:

  * Function and variable naming
  * Structural similarity
  * Programming-related semantics
* Using separate embedding models improves retrieval quality for:

  * Code-focused queries
  * Developer-centric search scenarios
* Maintaining separate FAISS indexes ensures:

  * Correct similarity comparisons
  * Clean isolation of embedding spaces
* Although this introduces additional complexity, it remains:

  * Manageable
  * Explicit
  * Justified by improved retrieval accuracy
* This design aligns with Recall AI’s goal of being a **high-quality personal knowledge and code recall system**, rather than a minimal prototype.

---

## Consequences

### Positive

* Improved semantic retrieval for both documents and code
* Clear separation of concerns
* Better alignment with real-world RAG system design
* Strong extensibility and future-proofing
* Demonstrates advanced system design choices suitable for production-scale thinking

### Negative

* Increased operational complexity (two models, two indexes)
* Slightly higher resource usage during indexing
* Additional logic required for query routing

---

## Implementation Notes - While searching kep this in mind.

* Embedding spaces must remain **fully isolated**
* Queries will be routed to:

  * Document index
  * Code index
  * Or both, based on user intent or query characteristics
* Index persistence will be handled independently for each embedding type
* The embedding layer will be abstracted to allow model replacement or upgrades
* **The user should be able to select to use only code or doc or both**

---

## Future Considerations

* Introduce query-time aggregation when searching both indexes
* Experiment with larger or domain-specific embedding models if scale increases
* Introduce hybrid ranking strategies if needed

