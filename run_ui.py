"""
Multi-Agent HR Intelligence Platform - Gradio UI Launcher

Simple script to launch the Gradio web interface.
"""

import sys
from pathlib import Path
import traceback

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("\n" + "=" * 70)
print("Multi-Agent HR Intelligence Platform - Customer Support Agent")
print("=" * 70)
print("\nPhase 2.2 - Professional Gradio Web Interface\n")

# Step 1: Initialize logging
print("[1/4] Initializing logging system...")
try:
    from src.utils import app_logger

    app_logger.info("Starting Multi-Agent HR Intelligence Platform Web Interface...")
    print("      [OK] Logger initialized")
except Exception as e:
    print(f"      [WARN] Logger failed: {e}")
    print("      --> Continuing without logging...")

# Step 2: Initialize database
print("\n[2/4] Initializing database...")
try:
    from src.database import init_db

    init_db()
    print("      [OK] Database ready!")
except Exception as e:
    print(f"      [WARN] Database initialization issue: {e}")
    print("      --> Continuing anyway (may work with defaults)...")

# Step 3: Load AI agent
print("\n[3/4] Loading AI agent...")
try:
    from src.main import get_customer_support_agent

    agent = get_customer_support_agent()
    print("      [OK] Agent ready!")
except Exception as e:
    print(f"      [FAIL] Agent loading failed: {e}")
    print("\n" + "=" * 70)
    print("ERROR DETAILS:")
    traceback.print_exc()
    print("=" * 70)
    print("\nTROUBLESHOOTING:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Check GROQ_API_KEY in .env file")
    print("  3. Run: python test_gradio.py for detailed diagnostics")
    print("=" * 70)
    sys.exit(1)

# Step 4: Start Gradio server
print("\n[4/4] Starting Gradio server...")
try:
    from src.ui.gradio_app import launch_app

    print("      [OK] Gradio module loaded")
    print("\n" + "=" * 70)
    print("SERVER STARTING")
    print("=" * 70)
    print("\n>>> URL: http://127.0.0.1:7860")
    print(">>> Mode: Local only (share=False)")
    print("\n[!] Press Ctrl+C to stop the server")
    print("=" * 70 + "\n")

    # Launch the app
    launch_app(
        server_name="127.0.0.1",  # Change to "0.0.0.0" for external access
        server_port=7860,
        share=False,  # Set to True to create a public share link
    )

except KeyboardInterrupt:
    print("\n\n" + "=" * 70)
    print("[!] Server stopped by user")
    print("=" * 70)
    sys.exit(0)

except Exception as e:
    print("\n" + "=" * 70)
    print("[ERROR] Failed to start Gradio server")
    print("=" * 70)
    print(f"\nError: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    print("\n" + "=" * 70)
    print("TROUBLESHOOTING:")
    print("=" * 70)
    print("1. Port 7860 may be in use:")
    print("   → Windows: netstat -ano | findstr :7860")
    print("   → Kill process: taskkill /PID <pid> /F")
    print("\n2. Run diagnostic test:")
    print("   → python test_gradio.py")
    print("\n3. Check dependencies:")
    print("   → pip install gradio==5.9.1")
    print("=" * 70)
    sys.exit(1)
