# ADR-001: Vector Store Selection

## Status
Accepted

## Context
Recall AI requires a local, offline vector store that supports fast similarity search,
persistence across restarts, and containerized deployment.

## Needs:
- I need a vectorDB which works great in my personal place and less maintaining overhead.
- Single user only. might open 2-5 terminals and ask queries.
- Should support meta-data filtering - like **"Search only in PDF"**
- Need Operational simplicity.
- Should work offline.
- Embedding persisted.

## Decision
We chose FAISS as the vector store for Recall AI.

## Alternatives Considered
- Qdrant

---

## Comparision:
| Feature               | FAISS                    | Qdrant                      |
| --------------------- | ------------------------ | --------------------------- |
| Type                  | Library                  | Database service            |
| Runs offline          | ✅ Yes                    | ⚠️ Yes (heavier)            |
| Setup                 | Very simple              | More complex                |
| Needs separate server | ❌ No                     | ✅ Yes                       |
| Metadata filtering    | ❌ No (manual)            | ✅ Yes                       |
| Persistence           | Manual save/load         | Built-in                    |
| Scalability           | Single-node              | Multi-node                  |
| Docker usage          | Very easy                | Extra container             |

#### - FAISS doesn't support Metadata filtering.
- Are we okay with this?
    - Still we can do post-retrival filtering, - this is enough for our usecase.
    - We can't do date based retrival - We are fine it.
    - We are not going to have Millions of chunks - so we can increase the number of chunks retrived and do post-filtering on it.
- We can avoid the setup choas by using the FAISS - thats great.
- We dont want to scale this since its a local service. 
- maintaining extra contianers is hard to debug - The procut should use friendly when they start using it we can expect people to setup Qrant and maintain all those things.
- We are fine to go with FAISS and use a extranl meta data filetering.



---

## Consequences
### Positive
- Simple deployment
- Fast query performance
- No background services required

### Negative
- No built-in metadata filtering
- Limited horizontal scalability

## Future Considerations
Qdrant may be considered if:
- Multi-user deployments are required
- Advanced filtering becomes necessary