# Quick Start Guide - Gradio UI

## Problem: "Connection Refused" Error

If you're getting "connection refused" when accessing http://127.0.0.1:7860, follow these steps:

## Solution Steps

### Step 1: Run the Diagnostic Test

```bash
python test_gradio.py
```

This will:
- Test all imports
- Initialize the database
- Load the AI agent
- Check port availability
- Launch the server with verbose logging

### Step 2: If Diagnostic Test Passes

The test will show you each step with [OK], [WARN], or [FAIL] status.

If all steps pass and the server starts, you'll see:
```
>>> Launching Gradio UI on http://127.0.0.1:7860
```

Open that URL in your browser!

### Step 3: If Port is In Use

If you see:
```
[WARN] Port 7860 is already in use
```

**Windows - Kill the process:**
```bash
# Find the process using the port
netstat -ano | findstr :7860

# Kill it (replace <PID> with the actual process ID)
taskkill /PID <PID> /F
```

**Or use a different port:**

Edit `test_gradio.py` or `run_ui.py` and change:
```python
port = 7861  # Use different port
```

### Step 4: Common Issues

#### Missing Dependencies

**Error:** `ModuleNotFoundError: No module named 'X'`

**Fix:**
```bash
pip install -r requirements.txt
```

#### Missing API Key

**Error:** `GROQ_API_KEY not found`

**Fix:**
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_api_key_here
```

#### Database Connection Error

**Error:** Database initialization failed

**Fix:**
```bash
# Initialize the database first
python initialize_kb.py
```

## Recommended Approach

### Option 1: Full Diagnostic (Recommended)

```bash
python test_gradio.py
```

**Pros:**
- Shows detailed progress
- Identifies exactly where failures occur
- Checks port availability
- Provides troubleshooting tips

### Option 2: Quick Launch

```bash
python run_ui.py
```

**Pros:**
- Simpler output
- Faster startup
- Good if you know everything works

## Expected Output (Success)

When successful, you should see:

```
======================================================================
GRADIO UI DIAGNOSTIC TEST
======================================================================

[STEP 1/6] Testing imports...
  [OK] Gradio imported successfully (version: 5.9.1)
  [OK] Logger imported successfully

[STEP 2/6] Initializing database...
  [OK] Database initialized successfully
  [OK] Database connection successful

[STEP 3/6] Loading AI agent...
  [OK] AI agent loaded successfully

[STEP 4/6] Creating Gradio interface...
  [OK] Gradio interface created successfully

[STEP 5/6] Checking port availability...
  [OK] Port 7860 is available

[STEP 6/6] Starting Gradio server...
======================================================================

>>> Launching Gradio UI on http://127.0.0.1:7860

... Starting server... (this may take a few seconds)
```

Then Gradio will show:
```
Running on local URL:  http://127.0.0.1:7860
```

## Troubleshooting Guide

### Issue: Server Starts But Can't Connect

**Symptoms:** Test says server is running, but browser shows "connection refused"

**Fixes:**
1. Check Windows Firewall - allow Python
2. Try 127.0.0.1 instead of localhost
3. Check browser isn't blocking local connections
4. Try a different browser

### Issue: Server Won't Start

**Symptoms:** Test fails at "Starting Gradio server..."

**Fixes:**
1. Check if another Gradio app is running
2. Restart your terminal
3. Try a different port (7861, 7862, etc.)
4. Check antivirus isn't blocking

### Issue: Slow Startup

**Symptoms:** Server takes 30+ seconds to start

**Explanation:** This is NORMAL on first run because:
- Loading LLM models
- Loading sentence transformers (300+ MB)
- Initializing vector database
- Connecting to Groq API

**Subsequent runs will be faster**

### Issue: Import Errors

**Symptoms:** `ModuleNotFoundError` during any step

**Fix:** Install missing packages:
```bash
# Core dependencies
pip install gradio==5.9.1
pip install langgraph langchain langchain-groq
pip install loguru

# Or install everything
pip install -r requirements.txt
```

## Files Created

1. **`test_gradio.py`** - Comprehensive diagnostic script
2. **`run_ui.py`** - Updated launcher with verbose logging
3. **`src/ui/gradio_app.py`** - Main Gradio interface (no changes needed)

## What Fixed the Original Issue?

The updated files now have:

[DONE] **Verbose logging** - See exactly what's happening
[DONE] **Step-by-step progress** - Know which step is failing
[DONE] **Port checking** - Detect and handle port conflicts
[DONE] **Error handling** - Graceful failures with helpful messages
[DONE] **Unicode fixes** - No emoji encoding errors on Windows

## Need More Help?

If you're still having issues:

1. Run diagnostic test and copy the full output
2. Check what step fails
3. Look at the error message
4. Check the troubleshooting section for that error

## Next Steps After Success

Once the server is running:

1. Open http://127.0.0.1:7860 in your browser
2. Type a test query: "My app keeps crashing"
3. See the AI response with:
   - Category badge
   - Sentiment indicator
   - Priority score
   - Knowledge base results
   - Processing time

Enjoy your Multi-Agent HR Intelligence Platform interface! 
