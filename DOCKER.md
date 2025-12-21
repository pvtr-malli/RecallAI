# Docker Quick Start

Run RecallAI with Docker in 3 simple steps.

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

## Quick Start

```bash
# 1. Configure folders in config.yaml or use Configure folders API call in the Frontend.
# 2. Generate docker-compose and start
make docker-up

# 3. Download LLM model (wait 10 seconds first)
make docker-pull-model

# 4. Access UI
open http://localhost:8000
```

## What This Does

- Starts two containers: `recallai-ollama` (LLM) and `recallai-app` (API + UI)
- Automatically mounts folders from `config.yaml`
- Downloads Llama 3.1 8B model (~4.5GB)
- Exposes UI at http://localhost:8000

## Folder Mounting

RecallAI automatically reads `config.yaml` and mounts your folders:

```yaml
# config.yaml
indexing:
  folders:
    - ~/Documents
    - ~/projects/code
```

These become `/data/folder_0`, `/data/folder_1` in Docker (paths auto-mapped).

## Common Commands

```bash
# View logs
make docker-logs

# Stop services
make docker-down

# Restart
docker-compose restart

# Complete reset
docker-compose down -v
rm -rf indexes models
```

## Troubleshooting

### Ollama Connection Error
Wait 10-15 seconds for Ollama to start, or check logs:
```bash
docker-compose logs ollama
```

### Model Not Found (404)
Pull the model:
```bash
make docker-pull-model
```

### Permission Errors
```bash
chmod 755 indexes models
```

## Data Persistence

Persisted data:
- **Ollama models**: Docker volume (~4.5GB)
- **Indexes**: `./indexes` (mounted from host)
- **Embedding models**: `./models` (mounted from host)
- **Config**: `./config.yaml` (mounted from host)

---
