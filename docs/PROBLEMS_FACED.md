# Missed during decision making;

## Choice of vector DB:
- Missed to consider that the FAISS soupport the vector deletion or not - because RecallAI gonna see this problem, becuse all this notes files can get updated.
- Qrant support the vector deletion internally - I should not need to implement the preodic cleanup there no **No orphan vectors**


# Implementation problems:
- 