"""
Vector Store implementation using FAISS for similarity search
"""

import os
import json
import pickle
from typing import List, Dict, Any, Optional
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from src.utils.logger import app_logger


class VectorStore:
    """
    Vector Store for managing document embeddings and similarity search
    Uses FAISS for efficient similarity search
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        index_path: str = "./data/knowledge_base/faiss_index",
        metadata_path: str = "./data/knowledge_base/metadata.json",
    ):
        """
        Initialize the Vector Store

        Args:
            model_name: Name of the sentence transformer model
            index_path: Path to save/load FAISS index
            metadata_path: Path to save/load document metadata
        """
        self.model_name = model_name
        self.index_path = index_path
        self.metadata_path = metadata_path

        # Initialize sentence transformer model
        app_logger.info(f"Loading embedding model: {model_name}")
        self.encoder = SentenceTransformer(model_name)
        self.embedding_dim = self.encoder.get_sentence_embedding_dimension()

        # Initialize FAISS index
        self.index: Optional[faiss.Index] = None
        self.documents: List[Dict[str, Any]] = []

        # Load existing index if available
        self.load()

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to the vector store

        Args:
            documents: List of document dictionaries
                Each dict should have: 'id', 'text', 'category', 'question', 'answer'
        """
        if not documents:
            app_logger.warning("No documents to add")
            return

        # Extract texts for embedding
        texts = [doc.get("text", "") for doc in documents]

        app_logger.info(f"Generating embeddings for {len(texts)} documents...")
        embeddings = self.encoder.encode(texts, show_progress_bar=True)
        embeddings = np.array(embeddings).astype("float32")

        # Create or update FAISS index
        if self.index is None:
            app_logger.info(
                f"Creating new FAISS index with dimension {self.embedding_dim}"
            )
            self.index = faiss.IndexFlatL2(self.embedding_dim)

        # Add embeddings to index
        self.index.add(embeddings)

        # Store document metadata
        self.documents.extend(documents)

        app_logger.info(
            f"Added {len(documents)} documents to vector store. Total: {len(self.documents)}"
        )

    def search(
        self, query: str, k: int = 3, category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents

        Args:
            query: Query text
            k: Number of results to return
            category_filter: Optional category to filter results

        Returns:
            List of similar documents with scores
        """
        if self.index is None or len(self.documents) == 0:
            app_logger.warning("Vector store is empty")
            return []

        # Generate query embedding
        query_embedding = self.encoder.encode([query])
        query_embedding = np.array(query_embedding).astype("float32")

        # Search in FAISS
        # Search more than k if we need to filter
        search_k = k * 3 if category_filter else k
        distances, indices = self.index.search(
            query_embedding, min(search_k, len(self.documents))
        )

        # Prepare results
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc["similarity_score"] = float(
                    1 / (1 + distance)
                )  # Convert distance to similarity

                # Apply category filter if specified
                if category_filter is None or doc.get("category") == category_filter:
                    results.append(doc)

                # Stop if we have enough results
                if len(results) >= k:
                    break

        app_logger.info(
            f"Found {len(results)} relevant documents for query: '{query[:50]}...'"
        )
        return results

    def save(self) -> None:
        """Save FAISS index and metadata to disk"""
        if self.index is None:
            app_logger.warning("No index to save")
            return

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        # Save FAISS index
        faiss.write_index(self.index, f"{self.index_path}.index")
        app_logger.info(f"Saved FAISS index to {self.index_path}.index")

        # Save metadata
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, indent=2, ensure_ascii=False)
        app_logger.info(f"Saved metadata to {self.metadata_path}")

    def load(self) -> bool:
        """
        Load FAISS index and metadata from disk

        Returns:
            True if loaded successfully, False otherwise
        """
        index_file = f"{self.index_path}.index"

        if not os.path.exists(index_file) or not os.path.exists(self.metadata_path):
            app_logger.info("No existing index found, starting fresh")
            return False

        try:
            # Load FAISS index
            self.index = faiss.read_index(index_file)
            app_logger.info(f"Loaded FAISS index from {index_file}")

            # Load metadata
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.documents = json.load(f)
            app_logger.info(
                f"Loaded {len(self.documents)} documents from {self.metadata_path}"
            )

            return True
        except Exception as e:
            app_logger.error(f"Error loading index: {e}")
            return False

    def clear(self) -> None:
        """Clear the vector store"""
        self.index = None
        self.documents = []
        app_logger.info("Cleared vector store")

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        return {
            "total_documents": len(self.documents),
            "embedding_dimension": self.embedding_dim,
            "model_name": self.model_name,
            "has_index": self.index is not None,
        }


def load_faqs_from_json(file_path: str) -> List[Dict[str, Any]]:
    """
    Load FAQs from JSON file and prepare for indexing

    Args:
        file_path: Path to FAQs JSON file

    Returns:
        List of processed documents
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = []
    for faq in data.get("faqs", []):
        # Combine question and answer for better retrieval
        text = f"Q: {faq['question']}\nA: {faq['answer']}"

        doc = {
            "id": faq["id"],
            "category": faq["category"],
            "question": faq["question"],
            "answer": faq["answer"],
            "text": text,  # Used for embedding
        }
        documents.append(doc)

    app_logger.info(f"Loaded {len(documents)} FAQs from {file_path}")
    return documents
