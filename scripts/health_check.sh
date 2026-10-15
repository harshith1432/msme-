#!/usr/bin/env bash
set -e

HOST="${1:-http://127.0.0.1:5000}"

echo "Running health checks against $HOST..."

LIVE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HOST/health/live")
if [ "$LIVE_STATUS" -eq 200 ]; then
    echo "✓ Liveness check passed (HTTP 200)"
else
    echo "✗ Liveness check failed (HTTP $LIVE_STATUS)"
    exit 1
fi

READY_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HOST/health/ready")
if [ "$READY_STATUS" -eq 200 ]; then
    echo "✓ Readiness check passed (HTTP 200)"
else
    echo "✗ Readiness check failed (HTTP $READY_STATUS)"
    exit 1
fi

echo "All system health checks passed."
