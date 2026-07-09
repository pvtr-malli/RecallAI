# RecallAI - Intelligent search for your local files

## Initial Thoughts/needs:
- The product should be able to search in all the folders I list.
- The supported file formates are - PDFs, .txt, All code files (Mostly I write in python - so ipynb,py), .md, 
- There should be a support to add file format also - if the file format is not supported give out a exception.
- I dont want to support Images - IMAGES NOT GONNA HAVE MUCH INFORMATION.
- While I search I want it to tell me the answer If I ask it to answer or I want to use it as a file searching also - Just point me the file where I have written down the notes, I'll go and check in the files.
- Should run in completely local and offline.
- Should be scallable using docker - I might open a second window and make multiple query to the server.
- Thinking of going as a API basis. will use FastAPI.
- A basic frontend or even a Clean CLI is also enugh for interaction.
- Re-index only when changed.
- Deletion should remove the chunks from the embedding space.
- I dont want the chuncking and embedding happening in the query time. It should happen separately when I start the server lets have a option to re-index manually at that time. then I can start making the queries.
- No multi language support needed -  the files will be in english only.

---

## 📄 **Recall AI — Requirements**

### 🎯 Core Functional Requirements

* The system **must search across user-specified folders** on the local machine.
* Supported file formats (initial scope):

  * **Text documents**: `.txt`, `.md`
  * **Code files**: `.py`, `.ipynb` (Python-first)
  * **Documents**: `.pdf`
* The system **must be extensible**:

  * New file formats can be added via configuration or code
  * If an unsupported format is encountered, the system should **raise a clear exception or warning**
* **Image files will not be supported**:

  * Rationale: Images usually contain little searchable semantic text for this use case
* **Indexing**:
  * Chunking and embedding **must not happen at query time**
  * Indexing must be **explicit and controlled**
  * Re-indexing happen only to **the modified files**.
  * All indexes must be **persisted across restarts**
  * Queries must be **fast and offline**
  * The system must be **scalable and container-friendly**

---

### 🔍 Search & Answering Behavior

* The system should support **two modes of interaction**:

  1. **Answer mode** – return a natural-language answer from the notes
  2. **Search mode** – return:

     * File name
     * File path
     * Relevant text snippet (optional)
* The user should be able to **explicitly choose the mode**, or the system should infer it from the query.

---

### 🧠 Retrieval & Intelligence

* The system should use **semantic search**, not just keyword matching.
* It should retrieve the **most relevant chunks** of text and:

  * Either answer the question
  * Or point to the relevant source files
* Source attribution (file path + chunk) is required for transparency.

---

### 🖥️ Runtime & Deployment

* The system must run **fully offline** and **locally**.
* No external APIs or cloud dependencies.
* The system should be **containerizable using Docker**.
* It should support **multiple concurrent queries** (e.g., multiple terminal windows or UI sessions).

---

### 🌐 Interface

* The primary interface will be an **API-based backend** using **FastAPI**.
* The API must expose endpoints for:

  * Index creation / re-indexing
  * Querying
  * Health checks
* The API must support multiple concurrent requests
* Interaction options:

  * A **clean CLI** (minimum requirement)
  * OR a **basic frontend UI** (optional)

---

### Non-Functional Requirements

* Low-latency query response
* Clear error handling and logging
* Configurable indexing parameters (chunk size, overlap, folders)
* Modular design to allow future extensions


---

### 🚫 Out of Scope (Initial Version)

* Image OCR
* Cloud-based LLMs
* Automatic background indexing
* Real-time file system monitoring
* User authentication
* No multi-language support needed.
---
