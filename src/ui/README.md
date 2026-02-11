# Multi-Agent HR Intelligence Platform - Gradio Web Interface

Professional web interface for the Multi-Agent HR Intelligence Platform customer support agent (Phase 2.2).

## Features

### 1. Beautiful Chat Interface
- Clean, modern design using Gradio Blocks
- Real-time message streaming
- User and assistant message bubbles
- Robot avatar for assistant messages

### 2. Real-Time Analysis Display
- **Category Badge**: Shows query category (Technical/Billing/Account/General)
- **Sentiment Badge**: Color-coded sentiment analysis
  -  Positive (Green)
  -  Neutral (Blue)
  -  Negative (Orange)
  -  Angry (Red)
- **Priority Score**: 1-10 scale with visual slider
- **Processing Time**: Shows response generation time
- **Escalation Status**: Warning badge when escalated to human agent

### 3. Knowledge Base Results
- Displays retrieved FAQ articles
- Shows similarity scores with color coding
- Expandable sections to view full FAQ content
- Category tags for each FAQ

### 4. Features Panel
- **User ID Input**: Set custom user identifier
- **System Status**: Real-time system health indicator
- **Statistics Display**:
  - Total queries processed
  - Average response time
  - Current user ID
- **Export Conversation**: Download chat history as JSON

### 5. Professional Styling
- Gradient header with brand colors
- Soft theme with indigo/purple accents
- Responsive layout
- Clean typography
- Smooth animations

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Knowledge Base (First Time Only)

```bash
python initialize_kb.py
```

### 3. Launch the Web Interface

```bash
python run_ui.py
```

The interface will be available at: http://127.0.0.1:7860

## Usage

### Basic Conversation

1. Enter your query in the text box
2. Click "Send" or press Enter
3. View the AI response in the chat window
4. Check the right panel for detailed analysis

### Features

#### Export Conversation
Click " Export JSON" to save the conversation history to a JSON file. The export includes:
- All messages
- Query analysis (category, sentiment, priority)
- Processing times
- Timestamps
- User information

#### User Identification
Enter a custom User ID in the "Settings" panel to track queries by user. This enables:
- Personalized conversation history
- VIP user detection
- Repeat query tracking

#### Clear Conversation
Click " Clear Conversation" to reset the chat and start fresh. This clears:
- Chat history
- Statistics
- Analysis displays

## Architecture

### Components

```
src/ui/
├── __init__.py          # Module exports
├── gradio_app.py        # Main Gradio interface
└── README.md            # This file
```

### Integration Points

The UI integrates with:
- `src.main.CustomerSupportAgent` - Main agent orchestrator
- `src.database` - Database initialization
- `src.utils` - Logging and utilities

### Session State

The interface maintains session-level state:
- Total queries processed
- Cumulative response time
- Conversation history
- Current user ID

## Configuration

### Server Settings

Edit `run_ui.py` to customize:

```python
launch_app(
    server_name="127.0.0.1",  # Change to "0.0.0.0" for external access
    server_port=7860,         # Change port number
    share=False               # Set True for public Gradio link
)
```

### Theme Customization

Edit `gradio_app.py` to customize colors:

```python
gr.themes.Soft(
    primary_hue="indigo",      # Main brand color
    secondary_hue="purple",    # Accent color
    neutral_hue="slate"        # Background color
)
```

### Sentiment Colors

Modify sentiment colors in `get_sentiment_color()`:

```python
colors = {
    "Positive": "#10b981",  # Green
    "Neutral": "#3b82f6",   # Blue
    "Negative": "#f59e0b",  # Orange
    "Angry": "#ef4444"      # Red
}
```

## API Reference

### Main Functions

#### `create_gradio_interface() -> gr.Blocks`
Creates and returns the Gradio Blocks interface.

#### `launch_app(server_name, server_port, share)`
Launches the Gradio application with specified settings.

**Parameters:**
- `server_name` (str): Server host address (default: "127.0.0.1")
- `server_port` (int): Server port number (default: 7860)
- `share` (bool): Create public share link (default: False)

### Helper Functions

#### `process_message(message, history, user_id)`
Processes user message and updates all interface elements.

**Returns:** Tuple of updated UI components

#### `format_category_badge(category) -> str`
Returns HTML badge for category display.

#### `format_sentiment_badge(sentiment) -> str`
Returns color-coded HTML badge for sentiment.

#### `format_kb_results(kb_results) -> str`
Formats knowledge base results as expandable HTML.

#### `export_conversation() -> str`
Exports conversation history to JSON file.

## Troubleshooting

### Interface Won't Start

**Error:** "System not initialized"

**Solution:** Ensure database is set up:
```bash
python initialize_kb.py
```

### No Knowledge Base Results

**Error:** "No KB articles found"

**Solution:** Load FAQs into knowledge base:
```bash
python initialize_kb.py
```

### Port Already in Use

**Error:** "Address already in use"

**Solution:** Change port in `run_ui.py`:
```python
server_port=7861  # Try different port
```

### Import Errors

**Error:** "ModuleNotFoundError"

**Solution:** Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Future Enhancements

Planned features for future versions:
- [ ] Multi-user chat support
- [ ] Conversation history browser
- [ ] Advanced analytics dashboard
- [ ] Theme switcher (light/dark mode)
- [ ] File upload for attachments
- [ ] Audio input/output
- [ ] Feedback collection
- [ ] A/B testing interface

## License

Part of the Multi-Agent HR Intelligence Platform project.

## Support

For issues or questions, please refer to the main project documentation.
