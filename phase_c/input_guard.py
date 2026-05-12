import time
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine
from shared.models import GuardResult
from shared.logger import get_logger

logger = get_logger("input_guard")

class InputGuard:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        self._add_vn_recognizers()
        
    def _add_vn_recognizers(self):
        # VN Phone Number
        vn_phone_pattern = Pattern(name="vn_phone", regex=r"(0[3|5|7|8|9])+([0-9]{8})\b", score=0.85)
        vn_phone_recognizer = PatternRecognizer(supported_entity="VN_PHONE", patterns=[vn_phone_pattern])
        self.analyzer.registry.add_recognizer(vn_phone_recognizer)
        
        # VN CCCD
        cccd_pattern = Pattern(name="vn_cccd", regex=r"\b([0-9]{12})\b", score=0.85)
        cccd_recognizer = PatternRecognizer(supported_entity="VN_CCCD", patterns=[cccd_pattern])
        self.analyzer.registry.add_recognizer(cccd_recognizer)

    async def check_pii(self, text: str) -> GuardResult:
        start_time = time.time()
        results = self.analyzer.analyze(text=text, entities=["EMAIL_ADDRESS", "VN_PHONE", "VN_CCCD", "US_SSN"], language='en')
        latency = (time.time() - start_time) * 1000
        
        if results:
            anonymized = self.anonymizer.anonymize(text=text, analyzer_results=results)
            logger.warning(f"PII detected. Anonymized text: {anonymized.text}")
            return GuardResult(is_safe=False, reason="PII detected", latency_ms=latency)
            
        return GuardResult(is_safe=True, reason="No PII detected", latency_ms=latency)
