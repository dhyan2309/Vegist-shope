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

$PY_CMD -m pip install -r requirements.txt
$PY_CMD manage.py collectstatic --noinput --clear

echo "=== BUILD END ==="
