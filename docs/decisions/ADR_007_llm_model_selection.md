# ADR-007: LLM Model and Quantization Choice

## Status

Accepted

---

## Context

RecallAI uses a local Large Language Model (LLM) to answer user questions based on retrieved local context (documents and code).
The LLM must operate:

* Fully **local and offline**
* The file content should not leave the laptop - privacy needed.
* With **limited system resources**
* As a **question-answering assistant**, not a text generator
* With predictable behavior and low latency

Two key decisions are required:

1. Whether to use a **base (pretrained)** model or an **instruction-tuned** model
2. Which **quantization level** to use for local inference

---

## Decision

RecallAI will use:

* An **instruction-tuned LLM**
* A **Q4 quantized version** of the model
* Deployed via **Ollama** for local inference

Specifically:

* **Model:** Llama 3.1 8B Instruct
* **Quantization:** Q4_0 (4-bit)
* **Deployment:** Ollama (`llama3.1:8b-instruct-q4_0`)

---

## Rationale

### Why Instruction-Tuned Model (Llama 3.1 8B Instruct)

Instruction-tuned models are trained to:

* Follow user instructions
* Answer questions directly
* Perform well on retrieval-augmented generation (RAG) tasks

RecallAI's primary task is:

> *"Answer my question using only the retrieved local context."*

Base (non-instruct) models:

* Generate raw text
* Require extensive prompt engineering to behave correctly
* May ignore instructions or hallucinate more easily

**Why Llama 3.1 8B Instruct:**

* Strong instruction following and reasoning capabilities
* Excellent performance on RAG tasks
* Good balance between model size (8B parameters) and quality
* Wide community support and documentation

Using an instruction-tuned model:

* Improves answer relevance
* Reduces prompt complexity
* Is better suited for retrieval-augmented generation (RAG)

---

### Why Q4_0 Quantization

Quantization reduces model size and memory usage by lowering numeric precision.

**Q4_0 (4-bit) quantization provides:**

* ~75% memory reduction compared to full precision (~4.5GB vs ~16GB)
* Faster inference on CPU
* Ability to run 8B models on consumer hardware
* Acceptable quality loss for question-answering tasks
* Median answer latency of ~2.4s on CPU

Higher precision (Q8):

* Uses significantly more memory (~8GB)
* Offers marginal quality improvement
* Increases latency and hardware requirements

Given RecallAI's local, offline constraints, Q4_0 offers the best trade-off.

### Why Ollama

Ollama provides:

* Simple model management (`ollama pull`, `ollama serve`)
* Automatic model quantization handling
* REST API for local inference
* Cross-platform support (macOS, Linux, Windows)
* No complex setup or configuration
* Built-in model caching and optimization

---

## Alternatives Considered

### Base (Non-Instruct) Models

* Rejected due to poor instruction following and higher prompt complexity

### Mistral-7B-Instruct

* Strong and efficient model
* Smaller (7B vs 8B parameters)
* Slightly weaker instruction adherence and reasoning compared to Llama 3.1 8B Instruct
* Less community support for RAG use cases

**Decision:** Chose Llama 3.1 8B Instruct for better RAG performance

### Q8 Quantization

* Better quality (~8GB model size)
* Higher memory usage
* Slower inference (~3-4s median latency)
* Not necessary for RecallAI's current QA-focused use case

**Decision:** Q4_0 provides acceptable quality with 2x faster inference

### Full Precision (FP16 / FP32)

* Not feasible for local deployment (~16GB+ model size)
* Excessive resource requirements
* Extremely slow on CPU

---

