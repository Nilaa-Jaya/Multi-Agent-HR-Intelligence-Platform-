# Multi-Agent HR Intelligence Platform - Setup Guide

##  Complete Setup Instructions

This guide will walk you through setting up Multi-Agent HR Intelligence Platform on your local machine.

## Prerequisites

- **Python 3.10 or higher**
- **Git** (for version control)
- **VS Code** (recommended) or any code editor
- **Groq API Key** (free at https://console.groq.com)

## Step-by-Step Setup

### 1. Get Your Groq API Key

1. Go to https://console.groq.com
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (you'll need it in step 4)

### 2. Download the Project

**If using VS Code locally:**

```bash
# Clone or download the project
cd /path/to/your/projects

# Create project directory
mkdir smartsupport-ai
cd smartsupport-ai

# Copy all files from the project here
```

### 3. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all necessary packages including:
- LangChain & LangGraph
- FastAPI & Uvicorn
- SQLAlchemy
- Gradio
- And more...

### 5. Configure Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Open .env in your editor
# Add your Groq API key
```

Edit `.env` file:
```
GROQ_API_KEY=your_actual_groq_api_key_here
SECRET_KEY=your-secret-key-change-this-to-something-random
DATABASE_URL=sqlite:///./smartsupport.db
```

**Important**: Replace `your_actual_groq_api_key_here` with your real Groq API key!

For SECRET_KEY, you can generate a random one:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 6. Initialize Database

```bash
python -c "from src.database import init_db; init_db()"
```

You should see: "Database initialized successfully"

### 7. Run Test Suite

```bash
python test_system.py
```

This will:
- Test database connection
- Test agent initialization
- Run 5 test queries
- Verify all components work correctly

### 8. Try the Example

```bash
python example.py
```

This runs example queries and shows you how to use the system.

### 9. Use in Your Code

Create a new Python file `my_test.py`:

```python
from src.database import init_db
from src.main import get_customer_support_agent

# Initialize (first time only)
init_db()

# Get agent
agent = get_customer_support_agent()

# Process a query
response = agent.process_query(
    query="How do I reset my password?",
    user_id="john_doe"
)

print(f"Category: {response['category']}")
print(f"Response: {response['response']}")
```

Run it:
```bash
python my_test.py
```

##  Development with VS Code

### Recommended VS Code Extensions

1. **Python** by Microsoft
2. **Pylance** by Microsoft
3. **Python Docstring Generator**
4. **SQLite Viewer**
5. **GitLens**

### VS Code Settings

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true
}
```

##  Project Structure Overview

```
smartsupport-ai/
├── src/
│   ├── agents/           # AI agents (categorizer, sentiment, etc.)
│   ├── database/         # Database models and queries
│   ├── utils/           # Config, logging, helpers
│   └── main.py          # Main orchestrator
├── test_system.py       # Test script
├── example.py           # Usage examples
├── requirements.txt     # Dependencies
├── .env                 # Your configuration (don't commit!)
└── README.md           # Documentation
```

##  Verify Installation

Run this quick check:

```python
# In Python interpreter
from src.utils.config import settings
print(f"API Key configured: {bool(settings.groq_api_key)}")
print(f"Database URL: {settings.database_url}")
```

##  Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution**: Make sure virtual environment is activated and dependencies installed
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: "API Key Error"
**Solution**: Check your `.env` file has the correct Groq API key
```bash
cat .env | grep GROQ_API_KEY
```

### Issue: "Database Error"
**Solution**: Initialize the database
```bash
python -c "from src.database import init_db; init_db()"
```

### Issue: "Import Error from src"
**Solution**: Run scripts from project root directory
```bash
cd smartsupport-ai
python test_system.py
```

##  Viewing the Database

To view your SQLite database:

**Option 1: VS Code Extension**
- Install "SQLite Viewer" extension
- Right-click `smartsupport.db` → "Open Database"

**Option 2: Command Line**
```bash
sqlite3 smartsupport.db
.tables
.schema conversations
SELECT * FROM conversations LIMIT 5;
.quit
```

##  Next Steps

1.  **Complete Phase 1** - You're here!
2.  **Add Knowledge Base** (Phase 2)
3.  **Build Gradio UI** (Phase 2)
4.  **Add Analytics Dashboard** (Phase 3)
5.  **Create REST API** (Phase 3)
6.  **Deploy with Docker** (Phase 4)

##  Learning Resources

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [LangGraph Guide](https://langchain-ai.github.io/langgraph/)
- [Groq API Docs](https://console.groq.com/docs/quickstart)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)

##  Tips

1. **Start Small**: Test with simple queries first
2. **Check Logs**: Look at `logs/app.log` for debugging
3. **Iterate**: Modify prompts in agent files to improve responses
4. **Experiment**: Try different query types and observe behavior
5. **Monitor**: Check database to see conversation history

##  Installation Checklist

- [ ] Python 3.10+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] Groq API key obtained
- [ ] `.env` file configured
- [ ] Database initialized
- [ ] Test script runs successfully
- [ ] Example script works
- [ ] Can process custom queries

##  You're Ready!

Once all checklist items are complete, you're ready to start building and improving Multi-Agent HR Intelligence Platform!

Need help? Check the README.md or create an issue on GitHub.

---

**Happy Coding! **
