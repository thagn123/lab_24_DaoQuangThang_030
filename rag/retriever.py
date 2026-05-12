from shared.config import config
from shared.logger import get_logger
from typing import List

logger = get_logger("retriever")

class RAGRetriever:
    def __init__(self):
        logger.info(f"Initializing RAG Retriever using Chroma DB from {config.CHROMA_DB_DIR}")
        
        self.embeddings = None
        self.vectorstore = None
        self.retriever = None
        
        try:
            from langchain_community.vectorstores import Chroma
            from langchain_community.embeddings import HuggingFaceEmbeddings
            
            self.embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
            self.vectorstore = Chroma(
                persist_directory=config.CHROMA_DB_DIR, 
                embedding_function=self.embeddings
            )
            self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": config.TOP_K})
            logger.info("ChromaDB and Embeddings loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load heavy dependencies (Chroma/HF): {e}.")
            logger.info("Falling back to mock retrieval mode.")

    async def get_relevant_contexts(self, query: str) -> List[str]:
        if config.MOCK_MODE or not self.retriever:
            logger.debug("Retrieving mock contexts.")
            return [
                "Mock context: AI and guardrails are essential for safety.", 
                "Mock context: Local LLMs provide privacy and cost benefits."
            ]
            
        try:
            docs = await self.retriever.ainvoke(query)
            return [doc.page_content for doc in docs]
        except Exception as e:
            logger.warning(f"Retrieval error: {e}. Returning mock.")
            return ["Error during retrieval. Using mock context."]
