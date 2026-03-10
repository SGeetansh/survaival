#!/usr/bin/env bash
set -euo pipefail

echo "Setting up Death by AI environment"

# -----------------------------
# Config
# -----------------------------
PYTHON_BIN="python3"
VENV_DIR=".venv"
MODEL_DIR="models"
REQUIREMENTS_FILE="requirements.txt"
ENTRYPOINT="play.py"

MODEL_NAME="Qwen2.5-7B-Instruct-Q4_K_M.gguf"
MODEL_URL="https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf?download=true"

# -----------------------------
# Sanity checks
# -----------------------------
command -v $PYTHON_BIN >/dev/null || {
  echo "python3 not found"
  exit 1
}

# -----------------------------
# Virtual environment
# -----------------------------
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment"
  $PYTHON_BIN -m venv "$VENV_DIR"
else
  echo "Virtual environment already exists"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# -----------------------------
# Dependencies
# -----------------------------
echo "Installing dependencies"
pip install --upgrade pip
pip install -r "$REQUIREMENTS_FILE"

# -----------------------------
# Model download
# -----------------------------
mkdir -p "$MODEL_DIR"

MODEL_PATH="$MODEL_DIR/$MODEL_NAME"

if [ ! -f "$MODEL_PATH" ]; then
  echo "⬇Downloading model: $MODEL_NAME"
  curl -L --fail "$MODEL_URL" -o "$MODEL_PATH"
else
  echo "Model already present"
fi

# -----------------------------
# Run game
# -----------------------------
echo "Launching game"
python "$ENTRYPOINT"
