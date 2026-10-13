#!/bin/bash
echo "=== BUILD START ==="

export PIP_BREAK_SYSTEM_PACKAGES=1

# Create and activate virtual environment to prevent externally-managed-environment errors
python3 -m venv .venv
source .venv/bin/activate

echo "Using virtualenv Python: $(python3 --version)"

# Install dependencies into virtual environment
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# Collect static files
python3 manage.py collectstatic --noinput --clear

echo "=== BUILD END ==="
