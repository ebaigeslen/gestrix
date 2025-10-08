#!/usr/bin/env bash
set -e

# === Fast Downward Setup Script ===
# Usage: bash scripts/setup_fastdownward.sh

echo "[Gestrix] Setting up Fast Downward..."

# Define install directory
FD_DIR="${FASTDOWNWARD_HOME:-$HOME/.cache/fastdownward}"

# Clone only if not already present
if [ ! -d "$FD_DIR" ]; then
  mkdir -p "$FD_DIR"
  git clone --depth 1 https://github.com/aibasel/downward.git "$FD_DIR"
fi

cd "$FD_DIR"

# Build with standard options
if [ ! -f "$FD_DIR/fast-downward.py" ]; then
  echo "[Gestrix] Building Fast Downward..."
  ./build.py -j2
else
  echo "[Gestrix] Fast Downward already built."
fi

# Export for GitHub Actions only (skip locally)
if [ -n "$GITHUB_ENV" ]; then
  echo "FASTDOWNWARD_HOME=$FD_DIR" >> "$GITHUB_ENV"
fi

echo "[Gestrix] Fast Downward setup complete at: $FD_DIR"
