#!/usr/bin/env bash
# Start City Thrift LP dashboard in demo mode (no cameras required)
set -e
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$PATH"

if ! python3 -c "import fastapi" 2>/dev/null; then
  echo "Installing dependencies..."
  pip install -r requirements.txt -q
fi

echo ""
echo "  City Thrift LP — Demo Mode"
echo "  No cameras or POS needed."
echo ""
echo "  Dashboard: http://127.0.0.1:8000"
echo "  (From another device on your network, use this PC's IP instead)"
echo ""
echo "  In a second terminal, run: python3 scripts/demo_simulator.py"
echo ""

exec python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
