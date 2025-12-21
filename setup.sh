#!/bin/bash

# RecallAI Setup Script
# One-time setup for RecallAI

set -e  # Exit on error

echo "=========================================="
echo "  RecallAI Setup"
echo "=========================================="
echo

# Check Python version
echo "🔍 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo "❌ Error: Python 3.11+ required. Found: $PYTHON_VERSION"
    exit 1
fi
echo "✅ Python $PYTHON_VERSION detected"
echo

# Check if Ollama is installed
echo "🔍 Checking for Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Installing Ollama..."
    echo

    # Detect OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            echo "Installing via Homebrew..."
            brew install ollama
        else
            echo "Installing via official script..."
            curl -fsSL https://ollama.com/install.sh | sh
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        echo "Installing via official script..."
        curl -fsSL https://ollama.com/install.sh | sh
    else
        echo "❌ Unsupported OS. Please install Ollama manually from https://ollama.com"
        exit 1
    fi
    echo "✅ Ollama installed"
else
    echo "✅ Ollama already installed"
fi
echo

# Start Ollama service (if not running)
echo "🔍 Checking Ollama service..."
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama service..."
    ollama serve > /dev/null 2>&1 &
    sleep 2
    echo "✅ Ollama service started"
else
    echo "✅ Ollama service already running"
fi
echo

# Pull the LLM model
echo "📥 Pulling Llama 3.1 8B Instruct model (this may take a few minutes)..."
if ollama list | grep -q "llama3.1:8b-instruct-q4_0"; then
    echo "✅ Model already downloaded"
else
    ollama pull llama3.1:8b-instruct-q4_0
    echo "✅ Model downloaded"
fi
echo

# Check if uv is installed
echo "🔍 Checking for uv..."
if ! command -v uv &> /dev/null; then
    echo "❌ uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    echo "✅ uv installed"
else
    echo "✅ uv already installed"
fi
echo

# Setup Python virtual environment with uv
echo "🐍 Setting up Python virtual environment with uv..."
if [ ! -d ".venv" ]; then
    uv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Install dependencies with uv
echo "📦 Installing Python dependencies with uv..."
uv pip install -e .
echo "✅ Dependencies installed"
echo

# Create default config if it doesn't exist
if [ ! -f "config.yaml" ]; then
    echo "📝 Creating default config.yaml..."
    cat > config.yaml << 'EOF'
# RecallAI Configuration

# Folders to index (comma-separated)
folders_to_index: []

# Model paths
models_dir: "models"

# Index storage
indexes_dir: "indexes"
db_path: "indexes/metadata.db"

# Supported file types
supported_extensions:
  documents:
    - ".txt"
    - ".md"
    - ".pdf"
  code:
    - ".py"
  notebooks:
    - ".ipynb"
EOF
    echo "✅ Default config.yaml created"
else
    echo "✅ config.yaml already exists"
fi
echo

echo "=========================================="
echo "  ✅ Setup Complete!"
echo "=========================================="
echo
echo "Next steps:"
echo
echo "1. Activate the virtual environment:"
echo "   source .venv/bin/activate"
echo
echo "2. Start RecallAI:"
echo "   python recall_ai/app.py"
echo
echo "3. Open your browser:"
echo "   http://localhost:8000"
echo
echo "=========================================="
