#!/bin/bash
# Start Flash Report servers
# Run this after DevSpace restart: bash start-servers.sh

# Kill existing processes
pkill -f "vite.*3000" 2>/dev/null
pkill -f "python3 upload_server.py" 2>/dev/null
sleep 1

# Start Vite (port 3000)
cd /home/paulosjr/.workspace/flash-report && npm run dev > /tmp/vite-flash.log 2>&1 &
echo "Vite started on port 3000"

# Start Upload Server (port 3003)
cd /home/paulosjr/.workspace/flash_report && ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" python3 upload_server.py > /tmp/upload-server.log 2>&1 &
echo "Upload server started on port 3003"

# Sync HTML
sleep 3
cp /home/paulosjr/.workspace/flash_report/flash-report.html /home/paulosjr/.workspace/flash-report/public/flash-report.html
echo "HTML synced"
echo ""
echo "Dashboard: https://ds-akyj2d5n--3000.us-east-1.prod.proxy.devspaces.amazon.dev/index.html"
echo "TinyURL:   https://tiny.amazon.com/r0aspqh7"
