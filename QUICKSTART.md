#  Quick Start Guide - Multi-Agent HR Intelligence Platform

##  Get Started in 5 Minutes

### Step 1: Get Groq API Key (2 minutes)
1. Go to https://console.groq.com
2. Sign up (free)
3. Get your API key from the dashboard

### Step 2: Setup Project (1 minute)
```bash
# In VS Code terminal or any terminal
cd smartsupport-ai
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Configure (30 seconds)
```bash
cp .env.example .env
# Edit .env and paste your Groq API key
```

### Step 4: Initialize (30 seconds)
```bash
python -c "from src.database import init_db; init_db()"
```

### Step 5: Test It! (1 minute)
```bash
# Run automated tests
python test_system.py

# Try interactive mode
python interactive.py

# Or run examples
python example.py
```

##  Quick Code Example

```python
from src.database import init_db
from src.main import get_customer_support_agent

# Setup (only once)
init_db()

# Get agent
agent = get_customer_support_agent()

# Ask a question!
response = agent.process_query(
    query="How do I reset my password?",
    user_id="my_user_id"
)

# Print response
print(f"Category: {response['category']}")
print(f"Response: {response['response']}")
```

##  What You Can Do Now

1. **Test Different Queries**
```python
queries = [
    "My app keeps crashing",
    "I was charged twice",
    "How do I delete my account?",
    "This is unacceptable! I want a refund!"
]

for query in queries:
    response = agent.process_query(query, user_id="test_user")
    print(f"\nQuery: {query}")
    print(f"Category: {response['category']}")
    print(f"Sentiment: {response['sentiment']}")
    print(f"Response: {response['response'][:100]}...")
```

2. **View Conversation History**
```python
history = agent.get_conversation_history("test_user", limit=5)
for conv in history:
    print(f"{conv['category']}: {conv['query']}")
```

3. **Check Database**
```python
from src.database import get_db_context, ConversationQueries

with get_db_context() as db:
    # Get statistics
    from src.database.queries import AnalyticsQueries
    summary = AnalyticsQueries.get_analytics_summary(db, days=7)
    print(summary)
```

##  Customize Prompts

Want better responses? Edit the prompts in:
- `src/agents/technical_agent.py`
- `src/agents/billing_agent.py`
- `src/agents/general_agent.py`

Example:
```python
# In technical_agent.py
TECHNICAL_PROMPT = ChatPromptTemplate.from_template(
    """You are an expert technical support agent...
    
    [Your custom instructions here]
    
    Response:"""
)
```

##  Troubleshooting

**"No module named 'src'"**
→ Make sure you're in the project directory and virtual environment is activated

**"API Key Error"**
→ Check your `.env` file has the correct Groq API key

**"Database Error"**
→ Run: `python -c "from src.database import init_db; init_db()"`

##  Learn More

- Full documentation: `README.md`
- Detailed setup: `SETUP.md`
- Project overview: `PROJECT_SUMMARY.md`

##  You're Ready!

Now you have a working AI customer support system! 

**Next:** Customize it, add features, and deploy it! 
