# ADR-007: LLM Model and Quantization Choice

## Status

Accepted

---

## Context

RecallAI uses a local Large Language Model (LLM) to answer user questions based on retrieved local context (documents and code).
The LLM must operate:

* Fully **local and offline**
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

Specifically:

* **Model type:** mistralai/Mistral-7B-Instruct
* **Quantization:** Q4 (4-bit)

---

## Rationale

### Why Instruction-Tuned Model - mistralai/Mistral-7B-Instruct

Instruction-tuned models are trained to:

* Follow user instructions
* Answer questions directly

RecallAI’s primary task is:

> *“Answer my question using only the retrieved local context.”*

Base (non-instruct) models:

* Generate raw text
* Require prompt engineering to behave correctly
* May ignore instructions or hallucinate more easily

Using an instruction-tuned model:

* Improves answer relevance
* Reduces prompt complexity
* Is better suited for retrieval-augmented generation (RAG)

---

### Why Q4 Quantization

Quantization reduces model size and memory usage by lowering numeric precision.

**Q4 (4-bit) quantization provides:**

* ~75% memory reduction compared to full precision
* Faster inference on CPU
* Ability to run 7B–8B models on consumer hardware
* Acceptable quality loss for question-answering tasks

Higher precision (Q8):

* Uses significantly more memory
* Offers marginal quality improvement
* Increases latency and hardware requirements

Given RecallAI’s local, offline constraints, Q4 offers the best trade-off.

---

## Alternatives Considered

### Base (Non-Instruct) Models

* Rejected due to poor instruction following and higher prompt complexity

### Mistral-7B-Instruct

* Strong and efficient
* Slightly weaker instruction adherence and reasoning compared to Llama-3.1-Instruct based on benchmarks from huggingface and practical evaluations

### Q8 Quantization

* Better quality
* Higher memory usage
* Not necessary for RecallAI’s current QA-focused use case

### Full Precision (FP16 / FP32)

* Not feasible for local deployment
* Excessive resource requirements

---

