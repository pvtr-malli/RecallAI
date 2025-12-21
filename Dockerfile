# RecallAI Dockerfile
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy project files
COPY pyproject.toml .
COPY recall_ai/ recall_ai/
COPY config.yaml .

# Install Python dependencies with uv
RUN /root/.local/bin/uv pip install --system -e .

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "recall_ai/app.py"]
