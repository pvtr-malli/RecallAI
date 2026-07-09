# FAISS Limitations and Workarounds

## The Deletion Problem

### Issue
FAISS indices **do not support deleting individual vectors**. This creates a problem when files are updated:

1. Old chunks are deleted from metadata DB ✅
2. New chunks and vectors are added ✅
3. **Old vectors remain in FAISS forever** ❌

Over time, this creates "orphaned" vectors that point to deleted chunks in the metadata.

### Why FAISS Can't Delete

FAISS is optimized for:
- Fast similarity search (millions of queries/second)
- Compact memory layout
- Efficient indexing algorithms (HNSW, IVF, etc.)

These optimizations require fixed-position vectors. Deleting would require:
- Rebuilding internal graph structures (HNSW)
- Recomputing cluster assignments (IVF)
- Updating all vector indices

This defeats the purpose of FAISS's speed.

## Current Solution: Periodic Rebuild

### How It Works

1. **Incremental updates** (default):
   ```bash
   POST /index
   ```
   - Skips unchanged files (hash-based)
   - Updates metadata for changed files
   - Adds new vectors to FAISS
   - ⚠️ Old vectors remain (creates garbage)

2. **Full rebuild** (periodic cleanup):
   ```bash
   POST /index?rebuild=true
   ```
   - Clears FAISS index completely
   - Clears metadata database
   - Re-indexes everything from scratch
   - ✅ No orphaned vectors

### When to Rebuild

Rebuild when:
- Many files have been updated/deleted
- Search results include outdated content
- FAISS index file is much larger than expected
- Periodic maintenance (e.g., weekly/monthly)

### Impact of Orphaned Vectors

**Minimal in most cases:**
- Search still works correctly (metadata filters out deleted chunks)
- FAISS index grows larger than necessary
- Slight performance impact (searches more vectors)
- Wasted disk space

**Example:**
- Original: 1000 chunks, 1000 vectors, 1.5 MB index
- After 100 updates: 1000 chunks, 1100 vectors, 1.65 MB index
- After rebuild: 1000 chunks, 1000 vectors, 1.5 MB index

## Alternative Solutions

### Option 1: IDMap Wrapper (Complex)
```python
index = faiss.IndexIDMap(faiss.IndexHNSWFlat(384, 32))
# Allows custom IDs, supports remove_ids()
# But: slower, more complex, loses some HNSW benefits
```

### Option 2: Lazy Deletion (Implemented)
```python
# Current approach:
# 1. Keep vectors in FAISS
# 2. Delete metadata entries
# 3. Filter at search time
# 4. Rebuild periodically
```

### Option 3: Multiple Indices
```python
# Rotate indices:
# - index_active.faiss (current)
# - index_old.faiss (being rebuilt)
# - Swap when rebuild complete
```

## Best Practices

1. **Enable rebuild in production**:
   - Add cron job: `curl -X POST http://localhost:8000/index?rebuild=true`
   - Schedule weekly or monthly

2. **Monitor index size**:
   ```python
   faiss_size_mb = os.path.getsize("indexes/documents.faiss") / 1024 / 1024
   total_chunks = metadata_store.get_total_chunks()
   vectors_per_chunk = faiss.get_count() / total_chunks
   # If ratio > 1.2, consider rebuilding
   ```

3. **Incremental updates for speed**:
   - Use default `/index` for frequent updates
   - User doesn't wait for full rebuild

4. **Rebuild for accuracy**:
   - Use `/index?rebuild=true` periodically
   - Removes all orphaned vectors

## Conclusion

The orphaned vector issue is a **known limitation of FAISS**, not a bug in RecallAI. The periodic rebuild approach is the recommended solution used by most FAISS-based systems in production.
