"""Knowledge retrieval system for PA bot."""

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import numpy as np

from src.core.logger import get_logger
from src.core.config import settings


logger = get_logger(__name__)


@dataclass
class Document:
    """Document with content and metadata."""
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None

    def __post_init__(self):
        """Calculate document hash for caching."""
        self.id = hash(self.content)


@dataclass
class RetrievalResult:
    """Result of document retrieval."""
    document: Document
    score: float
    rank: int


class KnowledgeRetriever:
    """
    Simple in-memory knowledge retriever using sentence embeddings.

    For production, this can be replaced with Qdrant or other vector databases.
    """

    def __init__(self, embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialize retriever.

        Args:
            embedding_model: HuggingFace model for embeddings
        """
        self.embedding_model_name = embedding_model
        self.model = None
        self.tokenizer = None
        self.documents: List[Document] = []
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.initialized = False

    async def initialize(self) -> None:
        """Load embedding model."""
        try:
            from sentence_transformers import SentenceTransformer

            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                self.executor,
                lambda: SentenceTransformer(self.embedding_model_name)
            )

            self.initialized = True
            logger.info("knowledge_retriever_initialized", model=self.embedding_model_name)

        except Exception as e:
            logger.warning("knowledge_retriever_init_failed", error=str(e))
            # Continue without embeddings - will use keyword fallback
            self.initialized = False

    async def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to the knowledge base with embeddings.

        Args:
            documents: List of documents to add
        """
        if not self.initialized or not self.model:
            logger.warning("retriever_not_initialized", action="documents_not_indexed")
            self.documents.extend(documents)
            return

        try:
            # Generate embeddings for all documents
            texts = [doc.content for doc in documents]

            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                self.executor,
                lambda: self.model.encode(texts, convert_to_numpy=True)
            )

            # Attach embeddings to documents
            for doc, embedding in zip(documents, embeddings):
                doc.embedding = embedding

            self.documents.extend(documents)
            logger.info("documents_added", count=len(documents), total=len(self.documents))

        except Exception as e:
            logger.error("document_embedding_failed", error=str(e))
            # Add without embeddings
            self.documents.extend(documents)

    async def retrieve(
        self,
        query: str,
        top_k: int = 3,
        threshold: float = 0.3
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: User query
            top_k: Number of top documents to return
            threshold: Minimum similarity score (0-1)

        Returns:
            List of retrieval results sorted by relevance
        """
        if not self.documents:
            logger.warning("no_documents_in_retriever")
            return []

        # Try semantic search with embeddings
        if self.initialized and self.model:
            try:
                return await self._semantic_search(query, top_k, threshold)
            except Exception as e:
                logger.error("semantic_search_failed", error=str(e))

        # Fallback to keyword search
        return await self._keyword_search(query, top_k)

    async def _semantic_search(
        self,
        query: str,
        top_k: int,
        threshold: float
    ) -> List[RetrievalResult]:
        """Semantic search using embeddings."""
        # Generate query embedding
        loop = asyncio.get_event_loop()
        query_embedding = await loop.run_in_executor(
            self.executor,
            lambda: self.model.encode(query, convert_to_numpy=True)
        )

        # Calculate cosine similarity with all documents
        scores = []
        for doc in self.documents:
            if doc.embedding is not None:
                # Cosine similarity
                similarity = np.dot(query_embedding, doc.embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(doc.embedding)
                )
                scores.append((doc, float(similarity)))
            else:
                scores.append((doc, 0.0))

        # Sort by score
        scores.sort(key=lambda x: x[1], reverse=True)

        # Filter by threshold and take top_k
        results = [
            RetrievalResult(document=doc, score=score, rank=i+1)
            for i, (doc, score) in enumerate(scores[:top_k])
            if score >= threshold
        ]

        logger.info(
            "semantic_search_completed",
            query_length=len(query),
            results_count=len(results),
            top_score=results[0].score if results else 0
        )

        return results

    async def _keyword_search(
        self,
        query: str,
        top_k: int
    ) -> List[RetrievalResult]:
        """Fallback keyword-based search."""
        query_lower = query.lower()
        query_words = set(query_lower.split())

        # Score documents by keyword overlap
        scores = []
        for doc in self.documents:
            doc_words = set(doc.content.lower().split())
            overlap = len(query_words & doc_words)
            score = overlap / max(len(query_words), 1)
            scores.append((doc, score))

        # Sort and take top_k
        scores.sort(key=lambda x: x[1], reverse=True)

        results = [
            RetrievalResult(document=doc, score=score, rank=i+1)
            for i, (doc, score) in enumerate(scores[:top_k])
            if score > 0
        ]

        logger.info(
            "keyword_search_completed",
            query_length=len(query),
            results_count=len(results)
        )

        return results

    def get_document_count(self) -> int:
        """Get total number of documents."""
        return len(self.documents)

    def clear_documents(self) -> None:
        """Clear all documents from retriever."""
        self.documents.clear()
        logger.info("documents_cleared")
