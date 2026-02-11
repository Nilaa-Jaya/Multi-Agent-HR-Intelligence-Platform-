"""
Simplified Gradio UI for Multi-Agent HR Intelligence Platform
This version uses fewer outputs to avoid Gradio type checking bugs
"""

import gradio as gr
from typing import List, Tuple
from src.main import get_customer_support_agent
from src.database import init_db
from src.utils import app_logger


# Initialize agent
agent = None


def init_agent():
    """Initialize the customer support agent"""
    global agent
    if agent is None:
        agent = get_customer_support_agent()
    return agent


def format_kb_results(kb_results: list) -> str:
    """Format knowledge base results as HTML"""
    if not kb_results:
        return "<p style='color: #6b7280; font-style: italic;'>No KB articles found</p>"

    html = "<div style='margin-top: 10px;'>"
    for i, result in enumerate(kb_results, 1):
        # KB retrieval agent returns: 'score', 'title', 'content', 'category'
        similarity = result.get("score", result.get("similarity_score", 0))
        title = result.get("title", result.get("question", "N/A"))
        category = result.get("category", "General")
        answer = result.get("content", result.get("answer", "No answer available"))

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


def process_message(message: str, history: List[Tuple[str, str]]):
    """
    Process user message and return updated chat history and metadata
    Returns: (updated_history, metadata_html, kb_results_html)
    """
    try:
        # Initialize agent if needed
        current_agent = init_agent()

        # Process the query
        result = current_agent.process_query(query=message, user_id="web_user")

        # Get response
        response_text = result.get(
            "response",
            "I apologize, but I encountered an error processing your request.",
        )

        # Update history
        history = history + [[message, response_text]]

        # Get metadata
        metadata = result.get("metadata", {})
        kb_results = metadata.get("kb_results", [])

        # Build metadata HTML
        category = result.get("category", "General")
        sentiment = result.get("sentiment", "Neutral")
        priority = result.get("priority", 5)
        processing_time = metadata.get("processing_time", 0)
        escalated = metadata.get("escalated", False)

        # Category color
        category_colors = {
            "Technical": "#3b82f6",
            "Billing": "#f59e0b",
            "Account": "#10b981",
            "General": "#6b7280",
        }
        category_color = category_colors.get(category, "#6b7280")

        # Sentiment color
        sentiment_colors = {
            "Positive": "#10b981",
            "Neutral": "#3b82f6",
            "Negative": "#f59e0b",
            "Angry": "#ef4444",
        }
        sentiment_color = sentiment_colors.get(sentiment, "#6b7280")

        # Build metadata display
        metadata_html = f"""
        <div style='padding: 15px; background-color: #f9fafb; border-radius: 8px; margin-bottom: 10px;'>
            <h4 style='margin-top: 0; color: #1f2937;'>Query Analysis</h4>
            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px;'>
                <div>
                    <p style='margin: 5px 0;'><strong>Category:</strong>
                    <span style='background-color: {category_color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;'>{category}</span></p>
                </div>
                <div>
                    <p style='margin: 5px 0;'><strong>Sentiment:</strong>
                    <span style='background-color: {sentiment_color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;'>{sentiment}</span></p>
                </div>
                <div>
                    <p style='margin: 5px 0;'><strong>Priority:</strong> {priority}/10</p>
                </div>
                <div>
                    <p style='margin: 5px 0;'><strong>Processing Time:</strong> {processing_time:.2f}s</p>
                </div>
            </div>
            {f'<p style="color: #ef4444; font-weight: 600; margin-top: 10px;">WARNING: Escalated: {metadata.get("escalation_reason", "")}</p>' if escalated else ''}
        </div>
        """

        # Format KB results
        kb_html = format_kb_results(kb_results)

        return history, metadata_html, kb_html

    except Exception as e:
        app_logger.error(f"Error processing message: {e}")
        import traceback

        traceback.print_exc()

        error_msg = f"Error: {str(e)}"
        history = history + [[message, error_msg]]
        metadata_html = "<p style='color: #ef4444;'>Error processing request</p>"
        kb_html = (
            "<p style='color: #6b7280; font-style: italic;'>No KB results available</p>"
        )

        return history, metadata_html, kb_html


def create_simple_interface():
    """Create simplified Gradio interface"""

    with gr.Blocks(title="Multi-Agent HR Intelligence Platform", theme=gr.themes.Soft()) as interface:

        gr.Markdown(
            """
            # Multi-Agent HR Intelligence Platform - Customer Support Agent

            Ask any question and get intelligent responses with knowledge base integration.
            """
        )

        with gr.Row():
            # Main chat area
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="Conversation", height=500, show_copy_button=True
                )

                msg_input = gr.Textbox(
                    label="Your Message",
                    placeholder="Type your question here...",
                    lines=2,
                )

                with gr.Row():
                    submit_btn = gr.Button("Send", variant="primary")
                    clear_btn = gr.Button("Clear")

            # Side panel
            with gr.Column(scale=1):
                gr.Markdown("###  Query Analysis")
                metadata_display = gr.HTML(
                    value="<p style='color: #6b7280;'>Submit a query to see analysis</p>"
                )

                gr.Markdown("###  Knowledge Base Results")
                kb_display = gr.HTML(
                    value="<p style='color: #6b7280; font-style: italic;'>Knowledge base results will appear here</p>"
                )

        # Footer
        gr.Markdown(
            """
            ---
            <div style='text-align: center; color: #6b7280; font-size: 12px;'>
                Multi-Agent HR Intelligence Platform v2.2 | Powered by LangGraph & Claude
            </div>
            """
        )

        # Event handlers
        msg_input.submit(
            fn=process_message,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, metadata_display, kb_display],
        ).then(fn=lambda: "", outputs=[msg_input])

        submit_btn.click(
            fn=process_message,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, metadata_display, kb_display],
        ).then(fn=lambda: "", outputs=[msg_input])

        clear_btn.click(
            fn=lambda: (
                [],
                "<p style='color: #6b7280;'>Submit a query to see analysis</p>",
                "<p style='color: #6b7280; font-style: italic;'>Knowledge base results will appear here</p>",
            ),
            outputs=[chatbot, metadata_display, kb_display],
        )

    return interface


def launch_simple_app(share=False, server_port=7860):
    """Launch the simplified Gradio app"""

    # Initialize database
    try:
        init_db()
        app_logger.info("Database initialized")
    except Exception as e:
        app_logger.warning(f"Database init warning: {e}")

    # Initialize agent
    init_agent()
    app_logger.info("Agent initialized")

    # Create and launch interface
    interface = create_simple_interface()

    app_logger.info("Launching simplified Multi-Agent HR Intelligence Platform Gradio interface...")

    interface.launch(
        server_name="127.0.0.1", server_port=server_port, share=share, show_error=True
    )


if __name__ == "__main__":
    launch_simple_app()
