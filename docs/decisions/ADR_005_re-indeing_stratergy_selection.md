# ADR-005: Indexing and Re-indexing Strategy

## Status

Accepted

---

## Context

Recall AI maintains vector indexes using FAISS along with metadata stored in SQLite.
As files evolve over time, the system must support **re-indexing** to reflect changes while balancing:

* Performance
* Implementation complexity
* Data consistency
* Operational simplicity

FAISS does not natively support efficient deletion or in-place updates of individual vectors, which complicates fine-grained re-indexing strategies.

---

## Decision

Recall AI adopts a **hybrid re-indexing approach** consisting of:

1. **Normal indexing mode (default)** for frequent updates
2. **Rebuild mode** for periodic cleanup and consistency restoration

This approach prioritizes **developer productivity and runtime efficiency** while keeping long-term index health manageable.

---
## What has been tried:
- Tried to implement full re-indeing by removing the vector also. but that was hapanning and damaged the vector store.
- option 2: Tried of doing a full clean of indexing and metadata each time. 
    - This is time consuming and I need to wait for the indexing to fininsh each time I want to use it.



---
## How It Works

### 1️⃣ Normal Indexing Mode (Default)

Triggered via:

```http
POST /index
```

Behavior:

* Skips files that are unchanged since the last index
* Deletes metadata entries for files that have changed
* Generates embeddings for new or modified files
* Adds new vectors to FAISS
* **Does not remove old vectors from FAISS**

Characteristics:

* Very fast
* Minimal computation
* Suitable for daily or frequent indexing

Tradeoff:

* Old vectors may remain in FAISS as **orphaned vectors**
* These vectors are not referenced by metadata and therefore do not affect retrieval correctness
* Minor memory overhead is accepted

---

### 2️⃣ Rebuild Mode (Periodic Cleanup)

Triggered via:

```http
POST /index?rebuild=true
```

Behavior:

* Clears the FAISS indexes (documents and code)
* Clears all metadata
* Re-indexes all configured files from scratch

Characteristics:

* Slower operation
* Higher compute cost
* Guarantees a clean, fully consistent index

Use cases:

* Weekly or monthly maintenance

---


## Future Considerations

* Introduce vector compaction during rebuilds
* Track orphaned vector count as a health metric
* Explore FAISS IDMap or external ID management if fine-grained deletion becomes necessary
* Automate rebuild scheduling if system usage grows

---

