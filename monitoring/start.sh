#!/bin/sh

export PATH="/usr/local/bin:$PATH"
export PYTHONUNBUFFERED=1

echo "🌸 Arrancando monitor..."
uv run --frozen python monitoring/monitor.py >> /tmp/monitor.log 2>&1 &

echo "🌸 Esperando 5s..."
sleep 5

tail -f /tmp/monitor.log &

echo "🌸 Arrancando Evidently UI..."
exec uv run --frozen evidently ui --workspace /workspace --host 0.0.0.0 --port 8000