#!/bin/bash
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
LOG_DIR="$ROOT/logs"
mkdir -p "$LOG_DIR"

echo "=== Flash Report Input App ==="
echo ""

# --- Backend ---
echo "[1/3] Installing Python dependencies..."
pip install -q -r "$BACKEND/requirements.txt"

echo "[2/3] Starting FastAPI backend on port 8000..."
pkill -f "uvicorn main:app" 2>/dev/null || true
(cd "$BACKEND" && uvicorn main:app --host 0.0.0.0 --port 8000 >> "$LOG_DIR/backend.log" 2>&1) &
BACKEND_PID=$!
echo "      Backend PID: $BACKEND_PID"

# --- Frontend ---
echo "[3/3] Installing Node dependencies and starting React on port 3000..."
cd "$FRONTEND"

if ! command -v node &>/dev/null; then
  echo "ERROR: Node.js not found. Please install Node.js >= 16"
  exit 1
fi

if [ ! -d node_modules ]; then
  npm install --prefer-offline >> "$LOG_DIR/npm-install.log" 2>&1
fi

pkill -f "react-scripts start" 2>/dev/null || true
BROWSER=none npm start >> "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "      Frontend PID: $FRONTEND_PID"

echo ""
echo "=== Waiting for services to start (30s) ==="
sleep 10

for i in $(seq 1 20); do
  if curl -sf http://localhost:8000/api/week >/dev/null 2>&1 && \
     curl -sf http://localhost:3000 >/dev/null 2>&1; then
    echo ""
    echo "Both services are up!"
    break
  fi
  echo -n "."
  sleep 1
done

echo ""
echo "============================================"
echo " Backend : http://localhost:8000"
echo " Frontend: http://localhost:3000"
echo " Logs    : $LOG_DIR/"
echo "============================================"
echo ""
echo "DevSpaces URL (port 3000):"
DEVSPACE_ID=$(cat /etc/devspace/id 2>/dev/null || echo "UNKNOWN")
PROXY_DOMAIN=$(cat /etc/devspace/http-proxy-base-domain 2>/dev/null || echo "UNKNOWN")
echo " https://${DEVSPACE_ID}--3000.${PROXY_DOMAIN}"
echo ""
