from shared.ollama_client import ollama_client
from shared.config import config
from shared.logger import get_logger

logger = get_logger("generator")

class RAGGenerator:
    def __init__(self):
        self.model_name = config.MODEL_RAG
        self.system_prompt = (
            "You are a helpful and precise assistant. "
            "Use the provided context to answer the user's question. "
            "If the answer is not in the context, say 'I don't know based on the context.' "
            "Do not hallucinate."
        )

    async def generate_answer(self, query: str, contexts: list[str]) -> str:
        context_str = "\\n\\n".join(contexts)
        prompt = f"Context:\\n{context_str}\\n\\nQuestion: {query}\\n\\nAnswer:"
        
        logger.debug(f"Generating answer using {self.model_name}")
        response = await ollama_client.generate(
            model=self.model_name,
            prompt=prompt,
            system=self.system_prompt
        )
        return response
