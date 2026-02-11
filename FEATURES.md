# Multi-Agent HR Intelligence Platform - Features Documentation

## Complete Feature List

### 1. Multi-Agent System Architecture

#### Query Categorization Agent
**Purpose**: Automatically classify customer queries into appropriate categories

**Categories Supported**:
- **Technical**: Software issues, bugs, crashes, configuration problems
- **Billing**: Payment issues, invoices, refunds, subscription management
- **Account**: Login problems, password resets, profile management, security
- **General**: Company information, policies, general inquiries

**How It Works**:
```python
# Uses LLM to analyze query and return category
query = "My app keeps freezing"
→ Category: "Technical"

query = "Why was I charged $50?"
→ Category: "Billing"
```

**Accuracy**: High accuracy with context-aware classification

---

#### Sentiment Analysis Agent
**Purpose**: Detect emotional tone and urgency of customer queries

**Sentiment Levels**:
- **Positive**: Happy, satisfied customers
- **Neutral**: Information-seeking, calm inquiries
- **Negative**: Disappointed, frustrated customers
- **Angry**: Very upset, demanding immediate attention

**Priority Calculation**:
```
Base Score: 5
+ Sentiment (Angry: +4, Negative: +3, Neutral: 0, Positive: -1)
+ Category (Technical/Billing: +1)
+ Repeat Query: +2
+ VIP Status: +2
= Priority Score (1-10)
```

**Example**:
```python
query = "This is ridiculous! Nothing works!"
→ Sentiment: "Angry"
→ Priority: 9/10 (High)
```

---

#### Specialized Response Agents

##### Technical Support Agent
- Provides step-by-step troubleshooting
- Explains technical concepts in simple terms
- Offers multiple solution approaches
- Escalates complex technical issues

##### Billing Support Agent
- Explains charges and billing cycles
- Handles refund requests professionally
- References company policies
- Escalates disputes appropriately

##### Account Support Agent
- Guides through password reset processes
- Addresses security concerns
- Helps with profile management
- Emphasizes account security

##### General Support Agent
- Answers company policy questions
- Provides information and resources
- Maintains friendly, professional tone
- Routes to specialists when needed

---

#### Escalation Agent
**Purpose**: Intelligently decide when human intervention is needed

**Escalation Triggers**:
1. High priority score (≥ 8/10)
2. Angry sentiment
3. Multiple unsuccessful attempts (≥ 3)
4. Escalation keywords detected:
   - "lawsuit", "legal", "lawyer"
   - "manager", "supervisor"
   - "unacceptable", "disgusted"
   - "cancel", "refund immediately"

**Escalation Response**:
- Empathetic acknowledgment
- Explains escalation process
- Provides case reference number
- Estimates wait time

---

### 2. LangGraph Workflow

**Workflow Stages**:
```
1. Query Input
   ↓
2. Categorization
   ↓
3. Sentiment Analysis
   ↓
4. Escalation Check
   ↓
5. Conditional Routing
   ├─→ Technical Agent
   ├─→ Billing Agent
   ├─→ Account Agent
   ├─→ General Agent
   └─→ Escalation Agent
   ↓
6. Response Generation
   ↓
7. Database Storage
```

**State Management**:
- Maintains context across workflow stages
- Tracks conversation history
- Preserves user context
- Records metadata

---

### 3. Database System

#### Tables Implemented

**Users Table**:
- User identification
- VIP status tracking
- Account creation timestamps

**Conversations Table**:
- Query and response storage
- Category and sentiment tracking
- Priority scores
- Escalation status
- Response time metrics

**Messages Table**:
- Individual message history
- Role identification (user/assistant)
- Timestamp tracking

**Feedback Table**:
- Rating collection (1-5 stars)
- Comment storage
- Helpfulness tracking
- Issue categorization

**Analytics Table**:
- Hourly aggregated metrics
- Query volume tracking
- Sentiment distribution
- Performance metrics

**Knowledge Base Table** (Ready for Phase 2)
- Article storage
- Category organization
- Tag system
- Usage statistics

#### Database Operations

**User Management**:
```python
# Get or create user
user = UserQueries.get_or_create_user(db, user_id="john_doe")

# Update VIP status
user.is_vip = True
```

**Conversation Tracking**:
```python
# Create conversation
conv = ConversationQueries.create_conversation(
    db, conversation_id, user_id, query, category, sentiment
)

# Update with response
ConversationQueries.update_conversation(
    db, conversation_id, response=response, status="Resolved"
)
```

**Analytics**:
```python
# Get summary statistics
summary = AnalyticsQueries.get_analytics_summary(db, days=7)
# Returns: total queries, avg response time, escalation rate, etc.
```

---

### 4. Context Management

#### Conversation History
- Stores last 5 messages per conversation
- Includes in LLM context for continuity
- Helps understand conversation flow
- Improves response relevance

#### User Context
- VIP status
- Repeat query detection
- Attempt count tracking
- Historical sentiment trends

**Example**:
```python
context = {
    "is_vip": True,
    "is_repeat_query": True,
    "attempt_count": 2
}
# Results in higher priority and special handling
```

---

### 5. Smart Routing

**Decision Logic**:
```python
if should_escalate:
    → Escalation Agent
elif category == "Technical":
    → Technical Agent
elif category == "Billing":
    → Billing Agent
elif category == "Account":
    → Account Agent
else:
    → General Agent
```

**Factors Considered**:
- Category classification
- Sentiment analysis
- Priority score
- Escalation triggers
- User history

---

### 6. Response Generation

**Context-Aware Responses**:
- Adapts tone to sentiment
- References conversation history
- Incorporates knowledge base (when available)
- Maintains brand voice

**Response Elements**:
1. Empathy acknowledgment (if needed)
2. Solution or information
3. Step-by-step instructions (if applicable)
4. Additional resources
5. Follow-up offer

**Example Response Flow**:
```
Query: "My app crashes when I export data"

1. Analysis:
   Category: Technical
   Sentiment: Neutral
   Priority: 6/10

2. Response includes:
   - Acknowledgment of issue
   - Troubleshooting steps
   - Alternative solutions
   - Offer to escalate if unresolved
```

---

### 7. Performance Tracking

**Metrics Collected**:
- Response time per query
- Category distribution
- Sentiment trends
- Escalation rates
- Resolution rates
- Customer satisfaction (via feedback)

**Analytics Functions**:
```python
# Get performance summary
summary = AnalyticsQueries.get_analytics_summary(db, days=7)

# Contains:
- total_queries: int
- avg_response_time: float
- escalation_rate: float (%)
- resolution_rate: float (%)
- avg_rating: float
- category_distribution: dict
- sentiment_distribution: dict
```

---

### 8. Error Handling

**Comprehensive Error Management**:
- Try-catch blocks in all agents
- Fallback responses
- Error logging
- Graceful degradation

**Example**:
```python
try:
    response = llm_manager.invoke(prompt, data)
except Exception as e:
    logger.error(f"LLM invocation failed: {e}")
    # Return fallback response
    return default_response
```

---

### 9. Logging System

**Log Levels**:
- INFO: Normal operations
- WARNING: Non-critical issues
- ERROR: Failures requiring attention
- DEBUG: Detailed troubleshooting info

**What's Logged**:
- Query processing steps
- Category and sentiment detection
- Routing decisions
- Response generation
- Database operations
- Errors and exceptions

**Log Location**: `logs/app.log`

---

### 10. Configuration Management

**Environment Variables**:
- API keys (Groq, OpenAI)
- Database URL
- Application settings
- LLM configuration
- Security settings

**Type-Safe Configuration**:
```python
from src.utils.config import settings

# Access configuration
model = settings.llm_model
temp = settings.llm_temperature
db_url = settings.database_url
```

---

##  Feature Comparison

### Current Features (Phase 1)
- Multi-agent architecture
- Query categorization
- Sentiment analysis
- Priority scoring
- Smart escalation
- Database persistence
- Conversation history
- Context management
- Error handling
- Logging system

###  Planned Features (Phase 2-4)
- Knowledge base with RAG
- Gradio web interface
- Multi-language support
- Real-time analytics dashboard
- REST API
- Webhook integration
- A/B testing framework
- Advanced analytics
- Docker deployment
- CI/CD pipeline

---

##  Use Cases

### 1. Technical Support
"My software won't update"
→ Provides troubleshooting steps

### 2. Billing Inquiries
"I see a charge I don't recognize"
→ Explains billing, offers to investigate

### 3. Account Issues
"I forgot my password"
→ Guides through reset process

### 4. Angry Customers
"This is unacceptable! I want a refund NOW!"
→ Escalates to human agent with context

### 5. VIP Customers
VIP status → Higher priority, special handling

---

##  Customization Options

### 1. Adjust Prompts
Edit agent files to customize responses:
- `src/agents/technical_agent.py`
- `src/agents/billing_agent.py`
- etc.

### 2. Modify Priority Scoring
Edit `src/utils/helpers.py`:
```python
def calculate_priority_score(...):
    # Adjust scoring logic
```

### 3. Add New Categories
1. Update categorization prompt
2. Create new agent
3. Add to workflow routing

### 4. Customize Escalation Triggers
Edit `src/utils/helpers.py`:
```python
def should_escalate(...):
    # Add custom logic
```

---

##  Performance Metrics

**Measured Automatically**:
- Processing time per query
- Database query performance
- LLM response time
- End-to-end latency

**Available Analytics**:
- Query volume over time
- Category distribution
- Sentiment trends
- Escalation patterns
- Response time averages

---

This comprehensive feature set makes Multi-Agent HR Intelligence Platform a professional, production-ready customer support system! 
