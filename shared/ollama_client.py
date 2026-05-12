import httpx
import asyncio
from typing import Dict, Any, Optional
from shared.config import config
from shared.logger import get_logger

logger = get_logger("ollama_client")

class OllamaClient:
    def __init__(self, base_url: str = config.OLLAMA_BASE_URL):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        self._check_mock_mode()
        
    def _check_mock_mode(self):
        if config.MOCK_MODE:
            logger.warning("OllamaClient initialized in MOCK MODE.")

    async def generate(self, model: str, prompt: str, system: Optional[str] = None, format: Optional[str] = None, retries: int = 3) -> str:
        if config.MOCK_MODE:
            return self._mock_response(model, format)
            
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        if system:
            payload["system"] = system
        if format:
            payload["format"] = format
            
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.post(url, json=payload, headers=self.headers)
                    response.raise_for_status()
                    return response.json().get("response", "")
            except httpx.RequestError as e:
                logger.error(f"Attempt {attempt + 1}/{retries} failed for Ollama generate: {e}")
                if attempt == retries - 1:
                    logger.error("All retries failed. Falling back to mock response.")
                    return self._mock_response(model, format)
                await asyncio.sleep(2 ** attempt) # Exponential backoff
        return self._mock_response(model, format)

    def _mock_response(self, model: str, format: Optional[str]) -> str:
        if format == "json":
            if model == config.MODEL_JUDGE:
                return '{"winner": "A", "reason": "Mocked JSON output", "accuracy": 4, "relevance": 4, "conciseness": 4, "helpfulness": 4}'
            elif model == config.MODEL_GUARD:
                return '{"safe": true, "reason": "Mock safe"}'
            else:
                return '{"result": "mock"}'
        return "This is a deterministic mock response generated because the Ollama endpoint is unreachable."

ollama_client = OllamaClient()
