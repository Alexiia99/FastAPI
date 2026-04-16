#!/bin/sh

export PATH="/usr/local/bin:$PATH"
export PYTHONUNBUFFERED=1

touch /tmp/monitor.log /tmp/approval.log

echo "🌸 Arrancando monitor..."
uv run --frozen python monitoring/monitor.py >> /tmp/monitor.log 2>&1 &

echo "🌸 Arrancando approval API..."
uv run --frozen uvicorn monitoring.approval_api:app --host 0.0.0.0 --port 8002 >> /tmp/approval.log 2>&1 &

tail -f /tmp/monitor.log /tmp/approval.log &

sleep 5

echo "🌸 Arrancando Evidently UI..."
exec uv run --frozen evidently ui --workspace /workspace --host 0.0.0.0 --port 8000