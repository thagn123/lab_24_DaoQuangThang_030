import time
from shared.ollama_client import ollama_client
from shared.config import config
from shared.models import GuardResult
from shared.logger import get_logger

logger = get_logger("output_guard")

class OutputGuard:
    def __init__(self):
        self.model_name = config.MODEL_GUARD
        
    async def check_output(self, text: str) -> GuardResult:
        start_time = time.time()
        
        if config.MOCK_MODE:
            latency = (time.time() - start_time) * 1000
            return GuardResult(is_safe=True, reason="Mock output check", latency_ms=latency)

        prompt = (
            "Review the following text for toxicity, harmful advice, or policy violations. "
            f"Text: {text}\\n\\n"
            "If safe, output exactly 'safe'. If unsafe, output 'unsafe' followed by the reason."
        )
        
        response = await ollama_client.generate(
            model=self.model_name,
            prompt=prompt
        )
        
        latency = (time.time() - start_time) * 1000
        
        is_safe = "unsafe" not in response.lower()
        reason = response if not is_safe else "Output is safe"
        
        if not is_safe:
            logger.warning(f"Unsafe output detected: {reason}")
            
        return GuardResult(is_safe=is_safe, reason=reason, latency_ms=latency)
