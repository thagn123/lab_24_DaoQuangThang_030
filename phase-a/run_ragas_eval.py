import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import json
import random
from shared.config import config
from shared.logger import get_logger

logger = get_logger("run_ragas")

def run_eval():
    logger.info("Running RAGAS evaluation (Mock metrics for local testing)")
    
    testset_path = os.path.join(config.BASE_DIR, "phase-a", "testset_v1.csv")
    if not os.path.exists(testset_path):
        logger.error("Testset not found. Run generate_testset.py first.")
        return
        
    df = pd.read_csv(testset_path)
    
    # Mocking RAGAS results
    df['answer'] = df['ground_truth'].apply(lambda x: x + " (Generated)")
    df['faithfulness'] = [random.uniform(0.7, 1.0) for _ in range(len(df))]
    df['answer_relevancy'] = [random.uniform(0.6, 1.0) for _ in range(len(df))]
    df['context_precision'] = [random.uniform(0.5, 1.0) for _ in range(len(df))]
    df['context_recall'] = [random.uniform(0.8, 1.0) for _ in range(len(df))]
    
    out_path = os.path.join(config.BASE_DIR, "phase-a", "ragas_results.csv")
    df.to_csv(out_path, index=False)
    
    summary = {
        "faithfulness": df['faithfulness'].mean(),
        "answer_relevancy": df['answer_relevancy'].mean(),
        "context_precision": df['context_precision'].mean(),
        "context_recall": df['context_recall'].mean(),
    }
    
    json_path = os.path.join(config.BASE_DIR, "phase-a", "ragas_summary.json")
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=4)
        
    logger.info(f"Evaluation complete. Summary: {summary}")

if __name__ == "__main__":
    run_eval()
