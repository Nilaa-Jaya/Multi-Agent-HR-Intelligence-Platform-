"""
Knowledge Base Retriever for searching and retrieving relevant FAQs
"""

from typing import List, Dict, Any, Optional
from src.knowledge_base.vector_store import VectorStore, load_faqs_from_json
from src.utils.logger import app_logger


class KnowledgeBaseRetriever:
    """
    Retriever for searching the knowledge base
    """

    def __init__(
        self,
        faq_path: str = "./data/knowledge_base/faqs.json",
        model_name: str = "all-MiniLM-L6-v2",
        auto_load: bool = True,
    ):
        """
        Initialize the Knowledge Base Retriever

        Args:
            faq_path: Path to FAQ JSON file
            model_name: Sentence transformer model name
            auto_load: Automatically load FAQs on initialization
        """
        self.faq_path = faq_path
        self.vector_store = VectorStore(model_name=model_name)

        if auto_load:
            self.load_faqs()

    def load_faqs(self) -> None:
        """Load FAQs into the vector store"""
        try:
            app_logger.info(f"Loading FAQs from {self.faq_path}")
            documents = load_faqs_from_json(self.faq_path)

            if documents:
                self.vector_store.add_documents(documents)
                self.vector_store.save()
                app_logger.info(f"Successfully loaded {len(documents)} FAQs")
            else:
                app_logger.warning("No FAQs found to load")

        except FileNotFoundError:
            app_logger.warning(f"FAQ file not found: {self.faq_path}")
        except Exception as e:
            app_logger.error(f"Error loading FAQs: {e}", exc_info=True)

    def retrieve(
        self,
        query: str,
        k: int = 3,
        category: Optional[str] = None,
        min_score: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant FAQs for a query

        Args:
            query: User query
            k: Number of results to retrieve
            category: Optional category filter
            min_score: Minimum similarity score threshold

        Returns:
            List of relevant FAQs with metadata
        """
        app_logger.info(f"Retrieving FAQs for query: '{query[:100]}...'")

        # Search vector store
        results = self.vector_store.search(query=query, k=k, category_filter=category)

        # Filter by minimum score
        filtered_results = [
            result
            for result in results
            if result.get("similarity_score", 0) >= min_score
        ]

        app_logger.info(
            f"Retrieved {len(filtered_results)} FAQs "
            f"(filtered from {len(results)} by score >= {min_score})"
        )

        return filtered_results

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        stats = self.vector_store.get_stats()
        stats["faq_path"] = self.faq_path
        return stats

    def reload_faqs(self) -> None:
        """Reload FAQs from disk (useful for updates)"""
        app_logger.info("Reloading FAQs...")
        self.vector_store.clear()
        self.load_faqs()


# Global retriever instance
_retriever: Optional[KnowledgeBaseRetriever] = None


def get_kb_retriever(
    faq_path: str = "./data/knowledge_base/faqs.json", force_reload: bool = False
) -> KnowledgeBaseRetriever:
    """
    Get or create knowledge base retriever singleton

    Args:
        faq_path: Path to FAQ JSON file
        force_reload: Force reload of FAQs

    Returns:
        KnowledgeBaseRetriever instance
    """
    global _retriever

    if _retriever is None:
        app_logger.info("Initializing Knowledge Base Retriever")
        _retriever = KnowledgeBaseRetriever(faq_path=faq_path)
    elif force_reload:
        _retriever.reload_faqs()

    return _retriever
