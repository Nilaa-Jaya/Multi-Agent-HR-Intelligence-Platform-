"""
Professional Gradio Web Interface for Multi-Agent HR Intelligence Platform - Phase 2.2

A beautiful, production-ready chat interface showcasing all AI capabilities.
"""

import gradio as gr
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional
import json
import time

from src.main import get_customer_support_agent
from src.database import init_db
from src.utils import app_logger


# Global state for session management
class SessionState:
    """Manage session-level state"""

    def __init__(self):
        self.total_queries = 0
        self.total_response_time = 0.0
        self.conversation_history: List[Dict[str, Any]] = []
        self.current_user_id = "anonymous"

    def add_query(self, response_time: float):
        """Track query statistics"""
        self.total_queries += 1
        self.total_response_time += response_time

    def get_avg_response_time(self) -> float:
        """Calculate average response time"""
        if self.total_queries == 0:
            return 0.0
        return self.total_response_time / self.total_queries

    def clear(self):
        """Clear session state"""
        self.total_queries = 0
        self.total_response_time = 0.0
        self.conversation_history = []


# Global session state
session_state = SessionState()

# Initialize agent
agent = None


def initialize_system():
    """Initialize database and agent on startup"""
    global agent
    try:
        app_logger.info("Initializing Multi-Agent HR Intelligence Platform system...")
        init_db()
        agent = get_customer_support_agent()
        app_logger.info("System initialized successfully!")
        return "System Ready", "[OK] Online"
    except Exception as e:
        app_logger.error(f"Failed to initialize system: {e}", exc_info=True)
        return f"Initialization Error: {str(e)}", "[FAIL] Offline"


def get_sentiment_color(sentiment: str) -> str:
    """Get color code for sentiment badge"""
    colors = {
        "Positive": "#10b981",  # Green
        "Neutral": "#3b82f6",  # Blue
        "Negative": "#f59e0b",  # Orange
        "Angry": "#ef4444",  # Red
    }
    return colors.get(sentiment, "#6b7280")  # Default gray


def format_category_badge(category: str) -> str:
    """Format HR category as HTML badge"""
    color_map = {
        "Recruitment": "#10b981",  # Green
        "Payroll": "#f59e0b",  # Orange
        "Benefits": "#3b82f6",  # Blue
        "Policy": "#6366f1",  # Indigo
        "LeaveManagement": "#8b5cf6",  # Purple
        "Performance": "#ec4899",  # Pink
        "General": "#6b7280",  # Gray
    }
    color = color_map.get(category, "#6b7280")
    return f'<span style="background-color: {color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">{category}</span>'


def format_sentiment_badge(sentiment: str) -> str:
    """Format sentiment as HTML badge with color coding"""
    color = get_sentiment_color(sentiment)
    return f'<span style="background-color: {color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">{sentiment}</span>'


def format_escalation_badge(escalated: bool) -> str:
    """Format escalation status as HTML badge"""
    if escalated:
        return '<span style="background-color: #ef4444; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">WARNING: ESCALATED</span>'
    return '<span style="background-color: #10b981; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">[OK] Resolved</span>'


def format_kb_results(kb_results: List[Dict[str, Any]]) -> str:
    """Format knowledge base results as HTML"""
    print(
        f"\n[format_kb_results] Received: {type(kb_results)}, length: {len(kb_results) if kb_results else 0}"
    )

    if not kb_results:
        print("[format_kb_results] No results - returning empty message")
        return "<p style='color: #6b7280; font-style: italic;'>No KB articles found</p>"

    print(f"[format_kb_results] Processing {len(kb_results)} results...")
    html = "<div style='margin-top: 10px;'>"
    for i, result in enumerate(kb_results, 1):
        print(f"  - Item {i}: {result}")

        # KB retrieval agent returns: 'score', 'title', 'content', 'category'
        # Support both old and new key names for backwards compatibility
        similarity = result.get("score", result.get("similarity_score", 0))
        title = result.get("title", result.get("question", "N/A"))
        category = result.get("category", "General")
        answer = result.get("content", result.get("answer", "No answer available"))

        print(
            f"    Extracted - score: {similarity}, title: {title[:50]}, category: {category}"
        )

        # Similarity score color
        if similarity >= 0.8:
            score_color = "#10b981"  # Green
        elif similarity >= 0.6:
            score_color = "#f59e0b"  # Orange
        else:
            score_color = "#ef4444"  # Red

        html += f"""
        <details style='margin-bottom: 15px; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; background-color: #f9fafb;'>
            <summary style='cursor: pointer; font-weight: 600; color: #1f2937;'>
                <span style='color: {score_color}; font-weight: 700;'>{similarity:.1%}</span> -
                {title}
                <span style='background-color: #e5e7eb; padding: 2px 8px; border-radius: 6px; font-size: 11px; margin-left: 8px;'>{category}</span>
            </summary>
            <div style='margin-top: 10px; padding: 10px; background-color: white; border-radius: 6px; color: #4b5563;'>
                {answer}
            </div>
        </details>
        """

    html += "</div>"
    return html


def process_message(message: str, history: List[Tuple[str, str]], user_id: str):
    """
    Process user message and return updated interface elements

    Returns:
        Tuple of (history, category_html, sentiment_html, priority_value, priority_number,
                 processing_time, escalation_html, kb_results_html, stats_html)
    """
    global agent, session_state

    if not message or not message.strip():
        return history, "", "", "", 0, "", "", "", ""

    if agent is None:
        error_msg = "System not initialized. Please refresh the page."
        history.append((message, error_msg))
        return history, "", "", "", 0, "", "", "", ""

    try:
        # Update session user ID
        session_state.current_user_id = user_id if user_id.strip() else "anonymous"

        # Process query
        start_time = time.time()
        result = agent.process_query(
            query=message, user_id=session_state.current_user_id
        )
        processing_time = time.time() - start_time

        # Debug: Print entire result structure
        print("\n" + "=" * 70)
        print("DEBUG: AGENT RESPONSE")
        print("=" * 70)
        print(f"Result keys: {list(result.keys())}")
        print(f"Result type: {type(result)}")

        # Extract response data
        response_text = result.get(
            "response", "I apologize, but I couldn't generate a response."
        )
        category = result.get("category", "General")
        sentiment = result.get("sentiment", "Neutral")
        priority = result.get("priority", 5)
        metadata = result.get("metadata", {})

        print(f"\nMetadata keys: {list(metadata.keys())}")
        print(f"Metadata type: {type(metadata)}")

        escalated = metadata.get("escalated", False)
        escalation_reason = metadata.get("escalation_reason", "")
        kb_results = metadata.get("kb_results", [])

        # Debug: Print KB results details
        print("\nKB Results:")
        print(f"  - Type: {type(kb_results)}")
        print(f"  - Length: {len(kb_results)}")
        print(f"  - Raw data: {kb_results}")
        if kb_results:
            print(f"  - First item keys: {list(kb_results[0].keys())}")
            print(f"  - First item: {kb_results[0]}")
        print("=" * 70 + "\n")

        # Debug logging for kb_results
        app_logger.info(f"[UI DEBUG] Metadata keys: {list(metadata.keys())}")
        app_logger.info(f"[UI DEBUG] KB results count: {len(kb_results)}")
        if kb_results:
            app_logger.info(f"[UI DEBUG] First KB result: {kb_results[0]}")
        else:
            app_logger.info("[UI DEBUG] No KB results found in metadata")

        # Update session state
        session_state.add_query(processing_time)
        session_state.conversation_history.append(
            {
                "query": message,
                "response": response_text,
                "category": category,
                "sentiment": sentiment,
                "priority": priority,
                "escalated": escalated,
                "timestamp": datetime.now().isoformat(),
                "processing_time": processing_time,
                "conversation_id": result.get("conversation_id", ""),
            }
        )

        # Update chat history
        history.append((message, response_text))

        # Format output elements
        category_html = format_category_badge(category)
        sentiment_html = format_sentiment_badge(sentiment)
        priority_html = f"{priority}/10"
        escalation_html = format_escalation_badge(escalated)
        if escalated and escalation_reason:
            escalation_html += f"<br><small style='color: #6b7280;'>Reason: {escalation_reason}</small>"

        # Debug: Print before formatting KB results
        print("\nDEBUG: About to format KB results")
        print(f"  - KB results to format: {kb_results}")
        print(f"  - Number of items: {len(kb_results)}")

        kb_results_html = format_kb_results(kb_results)

        print(f"  - HTML output length: {len(kb_results_html)}")
        print(f"  - HTML preview: {kb_results_html[:200]}...\n")

        # Format stats
        avg_time = session_state.get_avg_response_time()
        stats_html = f"""
        <div style='font-size: 14px; color: #4b5563;'>
            <p><strong>Total Queries:</strong> {session_state.total_queries}</p>
            <p><strong>Avg Response Time:</strong> {avg_time:.2f}s</p>
            <p><strong>Current User:</strong> {session_state.current_user_id}</p>
        </div>
        """

        return (
            history,
            category_html,
            sentiment_html,
            priority_html,
            priority,
            f"{processing_time:.2f}s",
            escalation_html,
            kb_results_html,
            stats_html,
        )

    except Exception as e:
        app_logger.error(f"Error processing message: {e}", exc_info=True)
        error_response = f"Error: {str(e)}"
        history.append((message, error_response))
        return history, "", "", "", 0, "", "", "", ""


def clear_conversation():
    """Clear conversation history"""
    global session_state
    session_state.clear()
    return [], "", "", "", 0, "", "", "", ""


def export_conversation() -> str:
    """Export conversation history as JSON"""
    global session_state

    if not session_state.conversation_history:
        return "No conversation to export"

    export_data = {
        "export_date": datetime.now().isoformat(),
        "user_id": session_state.current_user_id,
        "total_queries": session_state.total_queries,
        "avg_response_time": session_state.get_avg_response_time(),
        "conversations": session_state.conversation_history,
    }

    filename = f"conversation_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        return f"Conversation exported to {filename}"
    except Exception as e:
        return f"Export failed: {str(e)}"


def create_gradio_interface() -> gr.Blocks:
    """
    Create the main Gradio interface

    Returns:
        Gradio Blocks interface
    """

    # Custom CSS for professional styling
    custom_css = """
    .gradio-container {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    .header-title {
        text-align: center;
        color: #1f2937;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .header-subtitle {
        text-align: center;
        color: #6b7280;
        font-size: 16px;
        margin-bottom: 20px;
    }

    .info-panel {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
    }

    .stats-panel {
        background-color: #f9fafb;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }

    .priority-bar {
        height: 24px;
        background-color: #e5e7eb;
        border-radius: 12px;
        overflow: hidden;
    }

    #chatbot {
        height: 500px;
    }

    .kb-section {
        max-height: 400px;
        overflow-y: auto;
        padding: 10px;
        background-color: #ffffff;
        border-radius: 8px;
    }
    """

    with gr.Blocks(
        theme=gr.themes.Soft(
            primary_hue="indigo", secondary_hue="purple", neutral_hue="slate"
        ),
        css=custom_css,
        title="Multi-Agent HR Intelligence Platform - Employee Support Agent",
    ) as interface:

        # Header
        gr.Markdown(
            """
            <div class='header-title'>Multi-Agent HR Intelligence Platform</div>
            <div class='header-subtitle'>Intelligent HR Support Assistant - Your HR Questions Answered</div>
            """,
            elem_classes=["header"],
        )

        # Main layout
        with gr.Row():
            # Left column - Chat interface
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="Conversation",
                    height=500,
                    show_label=True,
                    elem_id="chatbot",
                    bubble_full_width=False,
                    avatar_images=(
                        None,
                        "https://em-content.zobj.net/source/twitter/376/robot_1f916.png",
                    ),
                )

                with gr.Row():
                    msg_input = gr.Textbox(
                        placeholder="Ask your HR question... (e.g., 'When is payday?', 'How do I request vacation?')",
                        show_label=False,
                        scale=4,
                        container=False,
                    )
                    send_btn = gr.Button("Send", variant="primary", scale=1)

                with gr.Row():
                    clear_btn = gr.Button("Clear Conversation", variant="secondary")
                    export_btn = gr.Button("Export JSON", variant="secondary")

                export_status = gr.Textbox(
                    label="Export Status", interactive=False, visible=False
                )

            # Right column - Information panels
            with gr.Column(scale=1):
                # User settings
                gr.Markdown("### Settings")
                user_id_input = gr.Textbox(
                    label="User ID", value="anonymous", placeholder="Enter your user ID"
                )

                system_status = gr.Textbox(
                    label="System Status", value="Initializing...", interactive=False
                )

                # Real-time information display
                gr.Markdown("###  Query Analysis")

                with gr.Group():
                    category_display = gr.HTML(
                        label="Category",
                        value="<p style='color: #6b7280;'>No query yet</p>",
                    )

                    sentiment_display = gr.HTML(
                        label="Sentiment",
                        value="<p style='color: #6b7280;'>No query yet</p>",
                    )

                    priority_display = gr.Textbox(
                        label="Priority Score", value="", interactive=False
                    )

                    priority_slider = gr.Slider(
                        minimum=1,
                        maximum=10,
                        value=0,
                        step=1,
                        label="Priority Level",
                        interactive=False,
                        show_label=False,
                    )

                    processing_time = gr.Textbox(
                        label="Processing Time", value="", interactive=False
                    )

                    escalation_display = gr.HTML(
                        label="Status",
                        value="<p style='color: #6b7280;'>No query yet</p>",
                    )

                # Statistics
                gr.Markdown("###  Statistics")
                stats_display = gr.HTML(
                    value="""
                    <div style='font-size: 14px; color: #4b5563;'>
                        <p><strong>Total Queries:</strong> 0</p>
                        <p><strong>Avg Response Time:</strong> 0.00s</p>
                        <p><strong>Current User:</strong> anonymous</p>
                    </div>
                    """
                )

        # Knowledge Base Results Section
        with gr.Row():
            with gr.Column():
                gr.Markdown("###  Knowledge Base Results")
                kb_results_display = gr.HTML(
                    value="<p style='color: #6b7280; font-style: italic;'>Knowledge base results will appear here</p>",
                    elem_classes=["kb-section"],
                )

        # Footer
        gr.Markdown(
            """
            ---
            <div style='text-align: center; color: #6b7280; font-size: 12px;'>
                Multi-Agent HR Intelligence Platform v2.2 | Powered by LangGraph & Claude |
                <a href='https://github.com' style='color: #8b5cf6;'>Documentation</a>
            </div>
            """
        )

        # Event handlers
        def submit_message(message, history, user_id):
            """Handle message submission"""
            return process_message(message, history, user_id)

        def handle_export():
            """Handle export button"""
            result = export_conversation()
            return {export_status: gr.update(value=result, visible=True)}

        # Connect event handlers
        msg_input.submit(
            fn=submit_message,
            inputs=[msg_input, chatbot, user_id_input],
            outputs=[
                chatbot,
                category_display,
                sentiment_display,
                priority_display,
                priority_slider,
                processing_time,
                escalation_display,
                kb_results_display,
                stats_display,
            ],
        ).then(fn=lambda: "", outputs=[msg_input])

        send_btn.click(
            fn=submit_message,
            inputs=[msg_input, chatbot, user_id_input],
            outputs=[
                chatbot,
                category_display,
                sentiment_display,
                priority_display,
                priority_slider,
                processing_time,
                escalation_display,
                kb_results_display,
                stats_display,
            ],
        ).then(fn=lambda: "", outputs=[msg_input])

        clear_btn.click(
            fn=clear_conversation,
            outputs=[
                chatbot,
                category_display,
                sentiment_display,
                priority_display,
                priority_slider,
                processing_time,
                escalation_display,
                kb_results_display,
                stats_display,
            ],
        )

        export_btn.click(fn=handle_export, outputs=[export_status])

        # Initialize system on load
        interface.load(fn=initialize_system, outputs=[export_status, system_status])

    return interface


def launch_app(
    server_name: str = "127.0.0.1", server_port: int = 7860, share: bool = False
):
    """
    Launch the Gradio application

    Args:
        server_name: Server host address
        server_port: Server port number
        share: Whether to create a public share link
    """
    app_logger.info("Launching Multi-Agent HR Intelligence Platform Gradio interface...")

    interface = create_gradio_interface()

    interface.launch(
        server_name=server_name,
        server_port=server_port,
        share=share,
        show_error=True,
        favicon_path=None,
    )


if __name__ == "__main__":
    # Launch with default settings
    launch_app(share=False)
