import time
from rag.retriever import RAGRetriever
from rag.generator import RAGGenerator
from shared.models import RAGResponse
from shared.logger import get_logger

logger = get_logger("rag_pipeline")

class RAGPipeline:
    def __init__(self):
        self.retriever = RAGRetriever()
        self.generator = RAGGenerator()

    async def ainvoke(self, query: str) -> RAGResponse:
        start_time = time.time()
        logger.info(f"Processing query: {query}")
        
        contexts = await self.retriever.get_relevant_contexts(query)
        answer = await self.generator.generate_answer(query, contexts)
        
        latency = (time.time() - start_time) * 1000
        logger.info(f"RAG pipeline completed in {latency:.2f} ms")
        
        return RAGResponse(
            answer=answer.strip(),
            contexts=contexts,
            source_documents=contexts, # Simplified
            latency_ms=latency
        )
