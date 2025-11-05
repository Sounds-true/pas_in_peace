"""Tests for RAG system."""

import pytest
from src.rag import KnowledgeRetriever, PAKnowledgeBase


@pytest.mark.asyncio
async def test_knowledge_base_loading():
    """Test knowledge base documents load."""
    docs = PAKnowledgeBase.get_all_documents()

    assert len(docs) > 10
    assert all(hasattr(d, 'content') for d in docs)
    assert all(hasattr(d, 'metadata') for d in docs)


@pytest.mark.asyncio
async def test_retriever_keyword_search():
    """Test keyword-based retrieval fallback."""
    retriever = KnowledgeRetriever()

    # Don't initialize (to use keyword fallback)
    docs = PAKnowledgeBase.get_all_documents()
    await retriever.add_documents(docs)

    results = await retriever.retrieve("что такое отчуждение", top_k=3)

    # Should find relevant docs even without embeddings
    assert len(results) > 0
