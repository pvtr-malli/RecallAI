# Running RecallAI with Docker

This guide covers running RecallAI using Docker and Docker Compose.

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

## Quick Start

### 1. Start Services

```bash
docker-compose up -d
```

This starts two containers:
- `recallai-ollama`: Ollama LLM service
- `recallai-app`: RecallAI application (API + UI)

### 2. Pull the LLM Model

**Wait for Ollama to start** (about 10 seconds), then pull the model:

```bash
docker exec recallai-ollama ollama pull llama3.1:8b-instruct-q4_0
```

This downloads ~4.5GB and takes a few minutes.

### 3. Access RecallAI

- **UI**: http://localhost:8000/
- **API Docs**: http://localhost:8000/docs

## Configuration

### Mounting Local Folders (Automatic from config.yaml)

**RecallAI automatically reads folders from `config.yaml` and mounts them in Docker!**

#### How It Works

1. **Configure folders** in `config.yaml`:
   ```yaml
   folders_to_index:
     - ~/Documents
     - ~/projects/code
     - ~/Desktop/notes
   ```

2. **Generate docker-compose** (automatic with `make docker-up`):
   ```bash
   python3 generate-docker-compose.py
   ```

3. **Folders are mounted** as `/data/folder_0`, `/data/folder_1`, etc.

4. **In RecallAI UI**, the paths are automatically correct!
   - `~/Documents` → `/data/folder_0`
   - `~/projects/code` → `/data/folder_1`
   - `~/Desktop/notes` → `/data/folder_2`

#### Manual Configuration (Legacy)

By default (if no folders in config.yaml), your home directory is mounted at `/host_home` (read-only). To index folders:

1. In the UI, use paths like: `/host_home/projects/notes`
2. Or edit `docker-compose.yml` to mount specific folders:

```yaml
volumes:
  - /path/to/your/notes:/data/notes:ro
  - /path/to/your/code:/data/code:ro
```

### Environment Variables

Configure via environment in `docker-compose.yml`:

```yaml
environment:
  - OLLAMA_BASE_URL=http://ollama:11434  # Already set
```

## Useful Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Just RecallAI app
docker-compose logs -f recallai

# Just Ollama
docker-compose logs -f ollama
```

### Stop Services

```bash
docker-compose down
```

### Restart Services

```bash
docker-compose restart
```

### Rebuild After Code Changes

```bash
docker-compose up -d --build
```

### Access Ollama Directly

```bash
# List models
docker exec recallai-ollama ollama list

# Run a test prompt
docker exec recallai-ollama ollama run llama3.1:8b-instruct-q4_0 "Hello"
```

## Data Persistence

The following are persisted in Docker volumes:

- **Ollama models**: `ollama_data` volume (~4.5GB)
- **Indexes**: `./indexes` directory (mounted from host)
- **Downloaded models**: `./models` directory (mounted from host)
- **Config**: `./config.yaml` (mounted from host)

To completely reset:

```bash
docker-compose down -v  # Remove volumes
rm -rf indexes models
```

## Architecture

```
┌─────────────────────────────────────────┐
│   Docker Host                           │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │  recallai-app (port 8000)          │ │
│  │                                    │ │
│  │  • FastAPI                         │ │
│  │  • Gradio UI                       │ │
│  │  • Embedding models                │ │
│  │  • FAISS indexes                   │ │
│  └────────────────┬───────────────────┘ │
│                   │ HTTP calls          │
│  ┌────────────────▼───────────────────┐ │
│  │  recallai-ollama (port 11434)     │ │
│  │                                    │ │
│  │  • Ollama service                  │ │
│  │  • Llama 3.1 8B Instruct           │ │
│  └────────────────────────────────────┘ │
│                                         │
│  Mounted volumes:                       │
│  • Your files (read-only)               │
│  • ./indexes (read-write)               │
│  • ./models (read-write)                │
└─────────────────────────────────────────┘
```

## Troubleshooting

### Ollama Connection Error

If you see "Cannot connect to Ollama":

1. Check if Ollama is running:
   ```bash
   docker ps | grep ollama
   ```

2. Check Ollama logs:
   ```bash
   docker-compose logs ollama
   ```

3. Wait a bit longer - Ollama takes 10-15 seconds to start

### Model Not Found (404 Error)

Pull the model:
```bash
docker exec recallai-ollama ollama pull llama3.1:8b-instruct-q4_0
```

### Permission Errors

Ensure mounted directories have correct permissions:
```bash
chmod 755 indexes models
```

### Out of Memory

The embedding models + LLM need ~8GB RAM. If Docker has insufficient memory:

1. Increase Docker memory limit (Docker Desktop → Settings → Resources)
2. Or use native setup instead (see README.md)

## Docker vs Native Setup

**Use Docker when:**
- ✅ You want containerized isolation
- ✅ You're familiar with Docker
- ✅ You want easy cleanup (just remove containers)

**Use Native when:**
- ✅ You want better performance
- ✅ You need direct file system access
- ✅ You prefer simpler debugging
- ✅ Your files are scattered across many locations

## Comparison

| Feature | Docker | Native |
|---------|--------|--------|
| Setup complexity | Medium | Simple |
| Performance | Good | Better |
| File access | Via mounts | Direct |
| Isolation | Strong | None |
| Memory usage | Higher | Lower |
| Cleanup | Easy | Manual |

## Next Steps

After starting with Docker:

1. **Configure folders** in the UI
2. **Index files** using the Index tab
3. **Search** your content

For more details, see [QUICKSTART.md](QUICKSTART.md).
