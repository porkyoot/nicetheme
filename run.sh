#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Change to the project root directory
cd "$(dirname "${BASH_SOURCE[0]}")"

# 1. Activate or Create Virtual Environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# 2. Install dependencies
echo "Installing/Updating package..."
pip install -e .
pip install watchfiles

# 3. Run the Python runner
echo "Starting application Runner..."
exec python3 run.py
