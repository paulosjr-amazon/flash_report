#!/bin/bash
# Healthcheck - restarts servers if they're down
# Add to crontab: * * * * * /home/paulosjr/.workspace/flash_report/keepalive.sh

# Check Vite (port 3000)
if ! curl -s -o /dev/null -w '' http://localhost:3000/ 2>/dev/null; then
    cd /home/paulosjr/.workspace/flash-report && /home/paulosjr/.local/share/mise/installs/node/24.15.0/bin/node node_modules/.bin/vite --host 0.0.0.0 --port 3000 > /tmp/vite-flash.log 2>&1 &
fi

# Check Upload Server (port 3003)
if ! curl -s -o /dev/null -w '' http://localhost:3003/api/datasets 2>/dev/null; then
    cd /home/paulosjr/.workspace/flash_report && ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" python3 upload_server.py > /tmp/upload-server.log 2>&1 &
fi
