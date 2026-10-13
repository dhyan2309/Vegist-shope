#!/bin/bash
echo "=== BUILD START ==="

if command -v python3 &>/dev/null; then
    PY_CMD=python3
elif command -v python &>/dev/null; then
    PY_CMD=python
else
    echo "ERROR: Python not found!"
    exit 1
fi

echo "Using: $($PY_CMD --version)"

# Install dependencies (bypass PEP 668 for ephemeral Vercel build container)
$PY_CMD -m pip install -r requirements.txt --break-system-packages || $PY_CMD -m pip install -r requirements.txt
$PY_CMD manage.py collectstatic --noinput --clear

echo "=== BUILD END ==="
