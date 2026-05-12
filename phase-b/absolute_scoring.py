import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import pandas as pd
from shared.ollama_client import ollama_client
from shared.config import config
from shared.utils import extract_json
from shared.logger import get_logger

logger = get_logger("absolute_scoring")

async def score_answer(q: str, a: str) -> dict:
    prompt = f"Question: {q}\\nAnswer: {a}\\nScore the answer on a scale of 1-5 for accuracy, relevance, conciseness, and helpfulness.\\nOutput JSON format required: {{\"accuracy\": 5, \"relevance\": 4, \"conciseness\": 3, \"helpfulness\": 4, \"reason\": \"...\"}}"
    res = await ollama_client.generate(model=config.MODEL_JUDGE, prompt=prompt, format="json")
    return extract_json(res)

async def run_scoring():
    data = [
        {"question": "How does AI detect fraud?", "answer": "It uses deep learning to detect anomalies globally."}
    ] * 10
    
    results = []
    for d in data:
        scores = await score_answer(d["question"], d["answer"])
        results.append({
            "question": d["question"],
            "answer": d["answer"],
            "accuracy": scores.get("accuracy", 3),
            "relevance": scores.get("relevance", 3),
            "conciseness": scores.get("conciseness", 3),
            "helpfulness": scores.get("helpfulness", 3),
            "reason": scores.get("reason", "")
        })
        
    df = pd.DataFrame(results)
    df.to_csv(os.path.join(config.BASE_DIR, "phase-b", "absolute_scores.csv"), index=False)
    logger.info("Saved absolute_scores.csv")

if __name__ == "__main__":
    asyncio.run(run_scoring())
