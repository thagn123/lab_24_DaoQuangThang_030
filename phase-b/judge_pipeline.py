import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import pandas as pd
from shared.ollama_client import ollama_client
from shared.config import config
from shared.utils import extract_json
from shared.logger import get_logger

logger = get_logger("judge_pairwise")

async def pairwise_judge(q: str, a1: str, a2: str) -> dict:
    prompt = f"Question: {q}\\nAnswer A: {a1}\\nAnswer B: {a2}\\nChoose the best answer based on accuracy, relevance, and helpfulness.\\nOutput JSON: {{\"winner\": \"A\" | \"B\" | \"tie\", \"reason\": \"...\"}}"
    res = await ollama_client.generate(model=config.MODEL_JUDGE, prompt=prompt, format="json")
    return extract_json(res)

async def run_pairwise():
    data = [
        {"question": "How does AI detect fraud?", "answer_a": "AI uses ML to find patterns.", "answer_b": "It uses deep learning to detect anomalies globally."}
    ] * 10
    
    results = []
    for d in data:
        # Run 1: A vs B
        res1 = await pairwise_judge(d["question"], d["answer_a"], d["answer_b"])
        winner1 = res1.get("winner", "tie")
        
        # Run 2: Swap B vs A to mitigate bias
        res2 = await pairwise_judge(d["question"], d["answer_b"], d["answer_a"])
        winner2_raw = res2.get("winner", "tie")
        winner2 = "A" if winner2_raw == "B" else "B" if winner2_raw == "A" else "tie"
        
        final_winner = winner1 if winner1 == winner2 else "tie"
        
        results.append({
            "question": d["question"],
            "answer_a": d["answer_a"],
            "answer_b": d["answer_b"],
            "run1_winner": winner1,
            "run2_winner": winner2_raw,
            "winner_after_swap": final_winner,
            "reason": res1.get("reason", "")
        })
        
    df = pd.DataFrame(results)
    os.makedirs(os.path.join(config.BASE_DIR, "phase-b"), exist_ok=True)
    df.to_csv(os.path.join(config.BASE_DIR, "phase-b", "pairwise_results.csv"), index=False)
    logger.info("Saved pairwise_results.csv")

if __name__ == "__main__":
    asyncio.run(run_pairwise())
