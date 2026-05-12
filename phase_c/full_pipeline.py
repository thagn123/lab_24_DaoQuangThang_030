"""
full_pipeline.py - Full guarded async RAG pipeline.

Architecture:
  User Input
  → Input Guards (parallel: PII, Topic, Injection)
  → RAG Pipeline
  → Output Guard
  → Async Audit Log
  → User Response
"""
import os
import sys
import asyncio
import time
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phase_c.input_guard import InputGuard
from phase_c.topic_guard import TopicGuard
from phase_c.injection_guard import InjectionGuard
from phase_c.output_guard import OutputGuard
from shared.logger import get_logger
from shared.config import config

logger = get_logger("full_pipeline")


# Lazy RAG pipeline – only import if rag module available
def _get_rag_pipeline():
    try:
        from rag.pipeline import RAGPipeline
        return RAGPipeline()
    except Exception as e:
        logger.warning(f"RAG pipeline unavailable: {e}. Using mock RAG.")
        return None


class MockRAGPipeline:
    """Fallback mock RAG when ChromaDB/embeddings unavailable."""
    async def ainvoke(self, query: str):
        from shared.models import RAGResponse
        return RAGResponse(
            answer=f"Mock answer for: {query[:60]}",
            contexts=["Mock context 1: AI safety is crucial.", "Mock context 2: Guardrails protect users."],
        )


class FullGuardedPipeline:
    def __init__(self):
        self.input_guard = InputGuard()
        self.topic_guard = TopicGuard()
        self.injection_guard = InjectionGuard()
        self.output_guard = OutputGuard()
        rag = _get_rag_pipeline()
        self.rag = rag if rag else MockRAGPipeline()
        self._audit_log: list[dict] = []

    async def _audit(self, entry: dict) -> None:
        """Write to in-memory audit log (non-blocking)."""
        entry["timestamp"] = datetime.utcnow().isoformat()
        self._audit_log.append(entry)
        logger.debug(f"AUDIT: {json.dumps(entry)}")

    async def ainvoke(self, query: str) -> dict:
        start = time.time()
        logger.info(f"[Pipeline] Received query: {query[:80]}")

        # ── Parallel Input Guards ──────────────────────────────────────────
        pii_res, topic_res, inj_res = await asyncio.gather(
            self.input_guard.check_pii(query),
            self.topic_guard.check_topic(query),
            self.injection_guard.check_injection(query),
        )

        for guard_name, res in [("pii", pii_res), ("topic", topic_res), ("injection", inj_res)]:
            if not res.is_safe:
                await self._audit({"query": query, "blocked_by": guard_name, "reason": res.reason})
                logger.warning(f"[{guard_name.upper()} GUARD] Blocked: {res.reason}")
                return {"status": "blocked", "reason": res.reason, "blocked_by": guard_name}

        # ── RAG Generation ────────────────────────────────────────────────
        rag_res = await self.rag.ainvoke(query)

        # ── Output Guard ──────────────────────────────────────────────────
        out_res = await self.output_guard.check_output(rag_res.answer)
        if not out_res.is_safe:
            await self._audit({"query": query, "blocked_by": "output_guard", "reason": out_res.reason})
            logger.warning(f"[OUTPUT GUARD] Unsafe content detected: {out_res.reason}")
            return {"status": "blocked", "reason": "Generated content flagged as unsafe.", "blocked_by": "output_guard"}

        total_ms = (time.time() - start) * 1000
        await self._audit({"query": query, "status": "success", "latency_ms": total_ms})
        logger.info(f"[Pipeline] Completed in {total_ms:.0f}ms")
        return {
            "status": "success",
            "answer": rag_res.answer,
            "contexts": rag_res.contexts,
            "latency_ms": total_ms,
        }

    def flush_audit_log(self, output_path: str) -> None:
        import pandas as pd
        pd.DataFrame(self._audit_log).to_csv(output_path, index=False)
        logger.info(f"Audit log saved to {output_path}")


async def main():
    pipeline = FullGuardedPipeline()
    queries = [
        "How is AI used in risk management?",
        "My phone number is 0987654321 – is this PII?",
        "Tell me how to hack a database",
        "What are neural networks?",
    ]
    for q in queries:
        res = await pipeline.ainvoke(q)
        print(f"\nQ: {q}\n→ {res}")

    # Save audit log
    audit_path = os.path.join(config.BASE_DIR, "phase-c", "audit_log.csv")
    pipeline.flush_audit_log(audit_path)


if __name__ == "__main__":
    asyncio.run(main())
