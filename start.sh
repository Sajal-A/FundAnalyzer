#!/bin/bash
# Start both Backend API and Frontend UI in separate tmux sessions
# Usage: bash start.sh

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Fund Performance Diagnostic AI - Full Stack Startup       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

echo "[1/3] Python found: $(python3 --version)"

# Check if tmux is available (optional)
if command -v tmux &> /dev/null; then
    echo "[2/3] Starting backend in tmux..."
    tmux new-session -d -s fund_backend -c "$PROJECT_ROOT" "python main.py"
    
    echo "[3/3] Starting frontend in tmux..."
    tmux new-session -d -s fund_frontend -c "$PROJECT_ROOT/frontend" "streamlit run app.py"
    
    echo ""
    echo "✓ Backend and frontend started in tmux sessions"
    echo ""
    echo "View sessions:"
    echo "  tmux list-sessions"
    echo ""
    echo "Attach to backend:  tmux attach -t fund_backend"
    echo "Attach to frontend: tmux attach -t fund_frontend"
    echo ""
else
    echo "[2/3] Starting backend (background)..."
    cd "$PROJECT_ROOT"
    python main.py > logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "✓ Backend started with PID: $BACKEND_PID"
    
    sleep 3
    
    echo "[3/3] Starting frontend..."
    cd "$PROJECT_ROOT/frontend"
    streamlit run app.py
    
    echo ""
    echo "Stopping backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    Startup Complete                           ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║                                                                ║"
echo "║  Backend API:  http://localhost:8000                          ║"
echo "║  API Docs:     http://localhost:8000/docs                     ║"
echo "║  Frontend UI:  http://localhost:8501                          ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
