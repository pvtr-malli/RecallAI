# ADR-008: Caching Strategy Decision

## Status

Rejected

---

## Context

RecallAI performs semantic search (~10ms) and LLM-based answers (~2.4s).

Caching could potentially store:
1. Query embeddings
2. Search results
3. LLM responses

**Question:** Should RecallAI implement caching (Redis, in-memory) to improve performance?

---

## Decision

**Do NOT implement caching.**

---

## Rationale

### 1. Search is Already Fast (<10ms)

* Median: **9.70ms**, P95: **11.66ms**
* Cache overhead (~1-2ms) provides negligible benefit
* Not worth the complexity

### 2. Low Cache Hit Rate Expected

* Single-user, exploratory queries (not repetitive)
* Users ask unique questions about their documents
* **Expected hit rate: <10%** - not worth it

### 3. LLM Inference is the Bottleneck

* Answer latency: **2.41s total** (2.3s LLM + 0.1s search)
* Caching search saves only **10ms out of 2410ms** (0.4%)
* Even caching LLM responses has low hit rate (~5%)

### 4. Cache Invalidation Complexity - so important.

* Files change frequently (re-indexing)
* Determining affected cached queries is non-trivial
* Stale cache results after re-indexing - need to have a clearing machanisum for this also.

---

## Alternatives Considered

### Redis Caching
* External dependency
* Operational complexity
* Low hit rate doesn't justify overhead

### In-Memory Caching (Python dict/LRU)
* Lost on restart
* Memory overhead for low-value cache
* Adds state management complexity

### LLM Response Caching Only
* Extremely low hit rate (<5%)
* Requires invalidation when docs change
* Natural language queries have slight variations

---

## Better Performance Improvements

Instead of caching:

1. **GPU Acceleration** - 5-10x faster LLM (~400ms vs 2.4s)
2. **Smaller Model** - Llama 3.1 3B: 2-3x faster (~800ms vs 2.4s)

---

## Consequences

By not implementing caching:

* ✅ Simple, offline-first architecture
* ✅ No external dependencies
* ✅ No cache invalidation complexity
* ✅ Lower memory footprint
* ✅ Easier to maintain

---