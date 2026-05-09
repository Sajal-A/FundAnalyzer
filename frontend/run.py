#!/usr/bin/env python
"""
frontend/run.py
────────────────
Starter script for the Streamlit UI.

Usage:
    python frontend/run.py              # Start the UI
    python frontend/run.py --host 0.0.0.0 --port 8501
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_streamlit(host: str = "localhost", port: int = 8501):
    """Run the Streamlit application."""
    
    frontend_dir = Path(__file__).parent
    app_file = frontend_dir / "app.py"
    
    if not app_file.exists():
        print(f"Error: app.py not found at {app_file}")
        sys.exit(1)
    
    print(f"🚀 Starting Fund Performance Diagnostic AI UI...")
    print(f"📊 UI will be available at http://{host}:{port}")
    print(f"💡 Make sure the backend API is running on http://localhost:8000")
    print()
    
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_file),
        "--server.address", host,
        "--server.port", str(port),
        "--server.headless", "false",
    ]
    
    subprocess.run(cmd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Start the Fund Performance Diagnostic AI UI"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind to (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Port to bind to (default: 8501)"
    )
    
    args = parser.parse_args()
    run_streamlit(host=args.host, port=args.port)
