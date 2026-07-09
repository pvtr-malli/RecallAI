# Missed during decision making;

## Choice of vector DB:
- Missed to consider that the FAISS soupport the vector deletion or not - because RecallAI gonna see this problem, becuse all this notes files can get updated.
- Qrant support the vector deletion internally - I should not need to implement the preodic cleanup there no **No orphan vectors**

# Implementation problems:
- Choosing a suitable embedding model.

# The choose of chinking:
- for futhur better understanding of each document - I should go for document specific chunking for each documents.
- can have agentic chunking methods for better grouping of informaitons into same chunks.
