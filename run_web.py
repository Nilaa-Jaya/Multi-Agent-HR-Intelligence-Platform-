"""
Launch Multi-Agent HR Intelligence Platform - FastAPI Web Interface
Production-ready alternative to Gradio
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("Multi-Agent HR Intelligence Platform - FastAPI Web Interface")
print("=" * 70)
print()
print("Version: 2.2.0")
print("Framework: FastAPI + Vanilla JavaScript")
print()

print("[1/3] Initializing logging...")
try:
    from src.utils import app_logger

    app_logger.info("Starting Multi-Agent HR Intelligence Platform FastAPI application...")
    print("      [OK] Logger initialized")
except Exception as e:
    print(f"      [WARN] Logger failed: {e}")

print("\n[2/3] Initializing database...")
try:
    from src.database import init_db

    init_db()
    print("      [OK] Database ready!")
except Exception as e:
    print(f"      [WARN] Database issue: {e}")

print("\n[3/3] Starting FastAPI server...")
try:
    from src.api import run_server

    print("\n" + "=" * 70)
    print("SERVER STARTING")
    print("=" * 70)
    print()
    print(">>> URL: http://127.0.0.1:8000")
    print(">>> API Docs: http://127.0.0.1:8000/docs")
    print(">>> Mode: Development (auto-reload enabled)")
    print()
    print("[!] Press Ctrl+C to stop the server")
    print("=" * 70)
    print()

    # Run server with auto-reload
    run_server(host="127.0.0.1", port=8000, reload=False)

except KeyboardInterrupt:
    print("\n\n[!] Server stopped by user")
except Exception as e:
    print(f"\n[ERROR] Failed to start: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
