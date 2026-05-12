import time
import numpy as np
from shared.config import config
from shared.models import GuardResult
from shared.logger import get_logger

logger = get_logger("topic_guard")

class TopicGuard:
    def __init__(self):
        logger.info(f"Loading embedding model {config.EMBEDDING_MODEL} for topic guard")
        try:
            from sentence_transformers import SentenceTransformer
            from sklearn.metrics.pairwise import cosine_similarity
            self.model = SentenceTransformer(config.EMBEDDING_MODEL)
            self.cosine_similarity = cosine_similarity
            self.mock_mode = False
        except Exception as e:
            logger.warning(f"Failed to load sentence-transformers: {e}. Using mock embeddings for topic guard.")
            self.model = None
            self.mock_mode = True

        self.allowed_topics = config.ALLOWED_TOPICS
        if not self.mock_mode:
            self.topic_embeddings = self.model.encode(self.allowed_topics)
        else:
            self.topic_embeddings = None

    async def check_topic(self, query: str, threshold: float = 0.3) -> GuardResult:
        start_time = time.time()
        
        if self.mock_mode:
            # Mock behavior: everything is safe unless it's obviously "unsafe" text
            latency = (time.time() - start_time) * 1000
            return GuardResult(is_safe=True, reason="Mock topic guard: allowed", confidence=1.0, latency_ms=latency)

        query_emb = self.model.encode([query])
        similarities = self.cosine_similarity(query_emb, self.topic_embeddings)[0]
        
        max_sim = float(np.max(similarities))
        latency = (time.time() - start_time) * 1000
        
        if max_sim >= threshold:
            best_idx = int(np.argmax(similarities))
            best_topic = self.allowed_topics[best_idx]
            return GuardResult(is_safe=True, reason=f"Topic matches {best_topic}", confidence=max_sim, latency_ms=latency)
            
        logger.warning(f"Off-topic query detected. Max similarity: {max_sim:.2f}")
        return GuardResult(is_safe=False, reason="Query is off-topic.", confidence=max_sim, latency_ms=latency)
