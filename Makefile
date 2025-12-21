.PHONY: help setup run docker-up docker-down docker-logs docker-pull-model clean

help:
	@echo "RecallAI - Available commands:"
	@echo ""
	@echo "  make setup           - Run initial setup (native)"
	@echo "  make run             - Start RecallAI (native)"
	@echo ""
	@echo "  make docker-up       - Start Docker services"
	@echo "  make docker-down     - Stop Docker services"
	@echo "  make docker-logs     - View Docker logs"
	@echo "  make docker-pull-model - Pull LLM model in Docker"
	@echo ""
	@echo "  make clean           - Clean indexes and models"

# Native setup
setup:
	@echo "Running setup..."
	./setup.sh

run:
	@echo "Starting RecallAI..."
	@. .venv/bin/activate && python recall_ai/app.py

# Docker commands
docker-up:
	@echo "Generating docker-compose.yml from config.yaml..."
	@python3 generate-docker-compose.py
	@echo ""
	@echo "Starting Docker services..."
	docker-compose up -d
	@echo "✅ Services started. Run 'make docker-pull-model' to download the LLM."

docker-down:
	@echo "Stopping Docker services..."
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-pull-model:
	@echo "Pulling Llama 3.1 8B Instruct model..."
	@echo "This may take a few minutes (~4.5GB download)..."
	docker exec recallai-ollama ollama pull llama3.1:8b-instruct-q4_0
	@echo "✅ Model downloaded"

# Clean up
clean:
	@echo "Cleaning indexes and models..."
	rm -rf indexes/*.faiss indexes/*.db models/*
	@echo "✅ Cleaned"
