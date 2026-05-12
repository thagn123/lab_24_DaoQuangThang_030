import pytest
import asyncio
from rag.pipeline import RAGPipeline

@pytest.mark.asyncio
async def test_rag_pipeline():
    pipeline = RAGPipeline()
    res = await pipeline.ainvoke("What is AI?")
    assert res.answer is not None
