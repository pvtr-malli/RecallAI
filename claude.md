# Claude Project Guide - RecallAI

## ⚠️ IMPORTANT: Read This First

**Before performing ANY task, making ANY code changes, or answering ANY questions about this project, you MUST:**

1. **Read [REQUIREMENTS.md](REQUIREMENTS.md)** to understand the complete project scope
2. **Verify your proposed changes align** with the stated requirements
3. **Check the constraints and out-of-scope items** to avoid unnecessary features

---

## 📋 Quick Reference

### Project Overview
RecallAI is an **intelligent local file search system** that enables semantic search across personal notes and code files, running completely offline.

### Core Principles
- ✅ **Offline-first**: No cloud dependencies, fully local
- ✅ **Pre-indexed**: Embeddings computed upfront, not at query time
- ✅ **Incremental**: Only re-index changed files
- ✅ **Fast**: Low-latency queries from pre-computed embeddings
- ✅ **Simple**: Clean API and CLI interface, no over-engineering

### Supported File Formats
- Text: `.txt`, `.md`
- Code: `.py`, `.ipynb`
- Documents: `.pdf`
- ❌ **NO Images** (by design)

### Technology Stack
- **Backend**: FastAPI
- **Deployment**: Docker
- **Interface**: API + CLI (frontend optional)
- **Search**: Semantic search with embeddings (local models)

### Key Features
1. **Two Query Modes**:
   - Answer mode: Natural language response
   - Search mode: File paths + snippets
2. **Explicit Indexing**: Manual trigger, not automatic
3. **Persistent Storage**: Indexes survive restarts
4. **Concurrent Queries**: Multi-session support

---

## 🚫 Out of Scope (Don't Implement)
- Image OCR
- Cloud-based LLMs
- Automatic background indexing
- Real-time file monitoring
- User authentication

---

## 🔄 Before Each Task

1. Read [REQUIREMENTS.md](REQUIREMENTS.md) if you haven't already
2. Confirm the task aligns with requirements
3. Keep solutions simple and focused
4. Avoid over-engineering or adding unrequested features

---

## 🎨 Code Style Guidelines

### Core Development Principles
**CRITICAL: Keep code simple and efficient - DO NOT over-engineer!**

- ✅ Write straightforward, readable code
- ✅ Optimize for efficiency when needed
- ❌ Avoid unnecessary abstractions
- ❌ Don't add features "for future flexibility"
- ❌ No premature optimization
- ❌ Keep it minimal and functional

**Rule of thumb:** If it's not explicitly required, don't build it.

### Function Docstrings
Always use this format for function docstrings:

```python
def function_name(param1: int, param2: str) -> bool:
    """
    Brief description of what the function does.

    param param1: Description of param1.
    param param2: Description of param2.
    """
```

**Requirements:**
- Always include type hints in function signature.
- Use multi-line docstring format (even for single line descriptions).
- Document parameters using `param parameter_name: description` format.
- Include return type hint (use `-> None` for void functions).

### Punctuation Rules
- Always end comments with a period (`.`).
- Always end list items in markdown files with a period (`.`).
- All sentences and descriptions must be properly punctuated.

### Type Hints (Python 3.13)
- Use built-in collection types directly: `list`, `dict`, `set`, `tuple`.
- DO NOT import from `typing` for basic collections.
- Use `typing` only for advanced types like `Optional`, `Union`, `Callable`, etc.

```python
# ✅ Correct (Python 3.9+).
def process_items(items: list[str]) -> dict[str, int]:
    pass

# ❌ Wrong - don't import List, Dict.
from typing import List, Dict
def process_items(items: List[str]) -> Dict[str, int]:
    pass
```

---

## 📁 Project Structure (To Be Established)

This section will be updated as the project structure is created.

---

**Remember**: Always consult [REQUIREMENTS.md](REQUIREMENTS.md) first!
