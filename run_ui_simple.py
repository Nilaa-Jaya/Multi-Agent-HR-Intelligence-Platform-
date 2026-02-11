"""
Simple launcher for Multi-Agent HR Intelligence Platform Gradio UI
This uses a simplified version to avoid Gradio type checking bugs
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("Multi-Agent HR Intelligence Platform - Customer Support Agent (Simplified UI)")
print("=" * 70)
print()

print("[1/3] Initializing logging...")
try:
    from src.utils import app_logger

    app_logger.info("Starting Multi-Agent HR Intelligence Platform Web Interface...")
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

print("\n[3/3] Launching simplified Gradio interface...")
try:
    from src.ui.gradio_app_simple import launch_simple_app

    print("\n" + "=" * 70)
    print("SERVER STARTING")
    print("=" * 70)
    print()
    print(">>> URL: http://127.0.0.1:7860")
    print(">>> Mode: Local only")
    print()
    print("[!] Press Ctrl+C to stop the server")
    print("=" * 70)
    print()

    launch_simple_app()

except KeyboardInterrupt:
    print("\n\n[!] Server stopped by user")
except Exception as e:
    print(f"\n[ERROR] Failed to start: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
