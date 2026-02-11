"""
Test script for Gradio UI with verbose logging and error handling
"""

import sys
from pathlib import Path
import traceback

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("\n" + "=" * 70)
print("GRADIO UI DIAGNOSTIC TEST")
print("=" * 70)

# Step 1: Test imports
print("\n[STEP 1/6] Testing imports...")
try:
    import gradio as gr

    print("  [OK] Gradio imported successfully (version: {})".format(gr.__version__))
except ImportError as e:
    print("  [FAIL] Failed to import Gradio:", str(e))
    print("  --> Run: pip install gradio")
    sys.exit(1)

try:
    from src.utils import app_logger

    print("  [OK] Logger imported successfully")
except ImportError as e:
    print("  [FAIL] Failed to import logger:", str(e))
    print("  --> Check src/utils/logger.py exists")
    sys.exit(1)

# Step 2: Test database initialization
print("\n[STEP 2/6] Initializing database...")
try:
    from src.database import init_db, get_db_context

    init_db()
    print("  [OK] Database initialized successfully")

    # Test database connection
    with get_db_context() as db:
        print("  [OK] Database connection successful")
except Exception as e:
    print("  [WARN] Database initialization failed:", str(e))
    print("  --> This may be okay if using SQLite")
    print("  --> Continuing anyway...")

# Step 3: Test agent loading
print("\n[STEP 3/6] Loading AI agent...")
try:
    from src.main import get_customer_support_agent

    agent = get_customer_support_agent()
    print("  [OK] AI agent loaded successfully")
except Exception as e:
    print("  [FAIL] Failed to load agent:")
    print("  ", str(e))
    traceback.print_exc()
    print("\n  --> Check if all LangChain dependencies are installed")
    print("  --> Run: pip install langchain langgraph langchain-groq")
    sys.exit(1)

# Step 4: Test Gradio interface creation
print("\n[STEP 4/6] Creating Gradio interface...")
try:
    from src.ui.gradio_app import create_gradio_interface

    interface = create_gradio_interface()
    print("  [OK] Gradio interface created successfully")
except Exception as e:
    print("  [FAIL] Failed to create interface:")
    print("  ", str(e))
    traceback.print_exc()
    sys.exit(1)

# Step 5: Check port availability
print("\n[STEP 5/6] Checking port availability...")
import socket


def is_port_available(port):
    """Check if a port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


port = 7860
if is_port_available(port):
    print(f"  [OK] Port {port} is available")
else:
    print(f"  [WARN] Port {port} is already in use")
    print(f"  --> Trying alternative port 7861...")
    port = 7861
    if is_port_available(port):
        print(f"  [OK] Port {port} is available")
    else:
        print(f"  [FAIL] Port {port} is also in use")
        print(f"  --> Kill any existing Python/Gradio processes")
        print(f"  --> Or specify a different port")

# Step 6: Launch Gradio
print("\n[STEP 6/6] Starting Gradio server...")
print("=" * 70)
print(f"\n>>> Launching Gradio UI on http://127.0.0.1:{port}")
print("\nServer configuration:")
print(f"  - Host: 127.0.0.1")
print(f"  - Port: {port}")
print(f"  - Share: False (local only)")
print(f"  - Show errors: True")
print("\n" + "=" * 70)
print("\n... Starting server... (this may take a few seconds)")
print("\n[!] Press Ctrl+C to stop the server")
print("=" * 70 + "\n")

try:
    interface.launch(
        server_name="127.0.0.1",
        server_port=port,
        share=False,
        show_error=True,
        favicon_path=None,
        inbrowser=False,  # Don't auto-open browser during test
    )
except Exception as e:
    print("\n" + "=" * 70)
    print("[ERROR] Failed to launch Gradio server")
    print("=" * 70)
    print(f"\nError message: {str(e)}")
    print("\nFull traceback:")
    traceback.print_exc()
    print("\n" + "=" * 70)
    print("TROUBLESHOOTING TIPS:")
    print("=" * 70)
    print("1. Check if port is already in use:")
    print("   --> Windows: netstat -ano | findstr :7860")
    print("   --> Kill process: taskkill /PID <pid> /F")
    print("\n2. Try a different port:")
    print("   --> Edit the 'port' variable in this script")
    print("\n3. Check firewall settings:")
    print("   --> Allow Python through Windows Firewall")
    print("\n4. Verify all dependencies:")
    print("   --> pip install -r requirements.txt")
    print("=" * 70)
    sys.exit(1)
