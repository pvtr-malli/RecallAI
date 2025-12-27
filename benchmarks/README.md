# RecallAI Performance Benchmarks

Performance testing scripts to measure latency metrics for RecallAI.

## Prerequisites

1. RecallAI must be running:
```bash
python recall_ai/app.py
```


## Benchmark Script

### API Latency Test

Measures pure API performance.

```bash
python benchmarks/latency_test.py
```

**What it measures**: Direct FastAPI endpoint latency.

**Use case**: Benchmark backend performance.

## Understanding UI Latency

**Why does the browser UI feel slower than the API benchmark?**

The API benchmark measures pure backend performance. When using the Gradio UI in a browser, you'll experience additional latency from:

- **Gradio Framework Overhead** (~50-100ms):
  - Network serialization/deserialization of the JSON
  - Middleware processing
  - Component state updates
  - Server-Sent Events (SSE) streaming

- **Browser Rendering** (~10-50ms):
  - DOM updates
  - Markdown rendering
  - Syntax highlighting

**Total UI Latency = API Latency + Gradio Overhead + Browser Rendering**

Example: ~8ms (API) + ~75ms (Gradio + Browser) = **~80-100ms user experience**

This is normal and expected for any web UI framework.

## What It Tests

The benchmark measures **min, max, p50, p90, p95** latency for:

- **Search mode**: 15 queries × 10 runs = 150 total requests
- **Answer mode**: 15 queries × 3 runs = 45 total requests (slower due to LLM)

## Test Queries

The scripts include 15 diverse queries covering various ML/AI topics:
- Multi-modality features and MLOps
- AI agents and tools
- Foundational models and factorization machines
- Multi-task classifiers
- Vertex AI and agent extensions

## Expected Results

### Search Mode (API)
- **P50**: <100ms
- **P90**: <150ms
- **P95**: <200ms

### Answer Mode (API)
- **P50**: 20-40 seconds
- **P90**: 40-60 seconds
- **P95**: 60-90 seconds

**Note**: Browser UI adds ~75-150ms overhead for search mode, negligible for answer mode.

## Output Format

```
============================================================
  SEARCH MODE - Latency Statistics (150 runs)
============================================================
  Min:    6.01ms
  Max:    114.82ms
  Mean:   8.49ms
  P50:    8.00ms
  P90:    9.39ms
  P95:    10.00ms
============================================================
```

## Customization

Edit [latency_test.py](latency_test.py) to:
- Add more test queries to `TEST_QUERIES` list
- Change `runs_per_query` (default: 10 for search, 3 for answer)
- Modify `top_k` parameter (default: 5)
- Change `search_in` parameter (default: "both")

## Notes

- Answer mode takes significantly longer due to LLM inference on CPU.
- Ensure you have indexed files before running benchmarks.
- Results vary based on CPU, RAM, and indexed corpus size.
- To measure real user-perceived latency, use browser dev tools (Network tab) while using the UI.
