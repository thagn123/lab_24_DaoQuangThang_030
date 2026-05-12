import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import time
from input_guard import InputGuard
from topic_guard import TopicGuard
from injection_guard import InjectionGuard
from output_guard import OutputGuard
from rag.pipeline import RAGPipeline
from shared.logger import get_logger

logger = get_logger("full_pipeline")

class FullGuardedPipeline:
    def __init__(self):
        self.input_guard = InputGuard()
        self.topic_guard = TopicGuard()
        self.injection_guard = InjectionGuard()
        self.output_guard = OutputGuard()
        self.rag = RAGPipeline()

    async def ainvoke(self, query: str) -> dict:
        logger.info(f"Received query: {query}")
        
        # Parallel Input Guards
        input_tasks = [
            self.input_guard.check_pii(query),
            self.topic_guard.check_topic(query),
            self.injection_guard.check_injection(query)
        ]
        pii_res, topic_res, inj_res = await asyncio.gather(*input_tasks)
        
        if not pii_res.is_safe:
            return {"status": "blocked", "reason": pii_res.reason}
        if not topic_res.is_safe:
            return {"status": "blocked", "reason": topic_res.reason}
        if not inj_res.is_safe:
            return {"status": "blocked", "reason": inj_res.reason}
            
        # RAG Generation
        rag_res = await self.rag.ainvoke(query)
        
        # Output Guard
        out_res = await self.output_guard.check_output(rag_res.answer)
        
        if not out_res.is_safe:
            return {"status": "blocked", "reason": "Output was flagged as unsafe."}
            
        return {"status": "success", "answer": rag_res.answer, "contexts": rag_res.contexts}

async def main():
    pipeline = FullGuardedPipeline()
    res = await pipeline.ainvoke("How is AI used in risk management?")
    print(res)

if __name__ == "__main__":
    asyncio.run(main())
