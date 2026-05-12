"""
topic_guard.py - Topic validation using Ollama embeddings.
Uses nomic-embed-text via Ollama API instead of sentence_transformers
to avoid Windows triton/torch compatibility issues.
"""
import os
import sys
import time
import json
import asyncio
import numpy as np
import httpx
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import config
from shared.models import GuardResult
from shared.logger import get_logger

logger = get_logger("topic_guard")

EMBED_MODEL = "nomic-embed-text"  # Lightweight Ollama embedding model


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    a_arr = np.array(a)
    b_arr = np.array(b)
    denom = np.linalg.norm(a_arr) * np.linalg.norm(b_arr)
    if denom == 0:
        return 0.0
    return float(np.dot(a_arr, b_arr) / denom)


def _mock_embed(text: str) -> list[float]:
    """Deterministic mock embedding based on character frequencies."""
    vec = [0.0] * 128
    for i, ch in enumerate(text[:128]):
        vec[i] = ord(ch) / 128.0
    return vec


async def _get_embedding(text: str) -> list[float]:
    """Fetch embedding from Ollama API. Falls back to mock on error."""
    if config.MOCK_MODE:
        return _mock_embed(text)
    url = f"{config.OLLAMA_BASE_URL}/api/embeddings"
    payload = {"model": EMBED_MODEL, "prompt": text}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("embedding", _mock_embed(text))
    except Exception as e:
        logger.warning(f"Ollama embedding failed: {e}. Using mock embedding.")
        return _mock_embed(text)


class TopicGuard:
    def __init__(self):
        self.allowed_topics = config.ALLOWED_TOPICS
        # Pre-compute topic embeddings synchronously at init using event loop
        logger.info(f"TopicGuard initialized. Allowed topics: {self.allowed_topics}")
        # Embeddings will be computed lazily on first use
        self._topic_embeddings: list[list[float]] | None = None

    async def _ensure_topic_embeddings(self) -> None:
        """Lazily compute and cache topic embeddings."""
        if self._topic_embeddings is None:
            logger.info("Computing topic embeddings...")
            self._topic_embeddings = []
            for topic in self.allowed_topics:
                emb = await _get_embedding(topic)
                self._topic_embeddings.append(emb)
            logger.info("Topic embeddings ready.")

    async def check_topic(self, query: str, threshold: float = 0.25) -> GuardResult:
        """
        Returns GuardResult indicating whether the query is on an allowed topic.

        Args:
            query: The user input string.
            threshold: Minimum cosine similarity to consider on-topic.

        Returns:
            GuardResult with is_safe=True if topic matches.
        """
        start_time = time.time()
        await self._ensure_topic_embeddings()

        query_emb = await _get_embedding(query)
        similarities = [
            _cosine_similarity(query_emb, topic_emb)
            for topic_emb in self._topic_embeddings
        ]
        max_sim = max(similarities) if similarities else 0.0
        best_idx = similarities.index(max_sim) if similarities else 0
        latency = (time.time() - start_time) * 1000

        if max_sim >= threshold:
            best_topic = self.allowed_topics[best_idx]
            logger.debug(f"Topic matched '{best_topic}' (sim={max_sim:.3f})")
            return GuardResult(
                is_safe=True,
                reason=f"Topic matches '{best_topic}' (similarity={max_sim:.2f})",
                confidence=max_sim,
                latency_ms=latency,
            )

        logger.warning(f"Off-topic query. Max similarity: {max_sim:.3f}")
        return GuardResult(
            is_safe=False,
            reason=f"Query is off-topic (max similarity={max_sim:.2f})",
            confidence=max_sim,
            latency_ms=latency,
        )


async def _test():
    guard = TopicGuard()
    result = await guard.check_topic("How does machine learning work?")
    print(result)
    result2 = await guard.check_topic("Tell me a joke about cats")
    print(result2)


if __name__ == "__main__":
    asyncio.run(_test())
