"""
Initialize Knowledge Base with FAQs
Run this script to load FAQs into the vector store
"""

from src.knowledge_base.retriever import get_kb_retriever
from src.utils.logger import app_logger


def main():
    """Initialize knowledge base"""
    print("=" * 60)
    print("Initializing Knowledge Base...")
    print("=" * 60)

    try:
        # Get retriever (will auto-load FAQs)
        retriever = get_kb_retriever(force_reload=True)

        # Get stats
        stats = retriever.get_stats()

        print(f"\nKnowledge Base Statistics:")
        print(f"- Total Documents: {stats['total_documents']}")
        print(f"- Embedding Model: {stats['model_name']}")
        print(f"- Embedding Dimension: {stats['embedding_dimension']}")
        print(f"- Has Index: {stats['has_index']}")
        print(f"- FAQ Path: {stats['faq_path']}")

        print("\n" + "=" * 60)
        print("Testing Knowledge Base Search...")
        print("=" * 60)

        # Test queries
        test_queries = [
            "My app keeps crashing",
            "How do I cancel my subscription?",
            "I forgot my password",
            "What are your business hours?",
        ]

        for query in test_queries:
            print(f"\nQuery: '{query}'")
            print("-" * 60)

            results = retriever.retrieve(query, k=2)

            if results:
                for i, result in enumerate(results, 1):
                    print(f"{i}. [{result['category']}] {result['question'][:60]}...")
                    print(f"   Score: {result['similarity_score']:.3f}")
            else:
                print("   No results found")

        print("\n" + "=" * 60)
        print("Knowledge Base Initialized Successfully!")
        print("=" * 60)
        print("\nYou can now use the customer support agent with RAG.")
        print("Try: python quick_test.py")

    except Exception as e:
        app_logger.error(f"Error initializing knowledge base: {e}", exc_info=True)
        print(f"\nError: {e}")
        print("Please check the logs for details.")


if __name__ == "__main__":
    main()
