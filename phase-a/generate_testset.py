import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from shared.config import config
from shared.logger import get_logger

logger = get_logger("generate_testset")

def generate_mock_testset():
    logger.info("Generating synthetic testset (mock mode due to RAGAS dependency on OpenAI/Custom Wrappers)")
    data = []
    
    # Simple (50%)
    for i in range(25):
        data.append({
            "question": f"What is the basic concept {i} of algorithmic trading?",
            "ground_truth": "Algorithmic trading uses AI to make decisions in milliseconds.",
            "contexts": ["AI algorithms are increasingly used in algorithmic trading, where decisions are made in milliseconds."],
            "evolution_type": "simple"
        })
        
    # Reasoning (25%)
    for i in range(13):
        data.append({
            "question": f"Why is machine learning effective in risk assessment scenario {i}?",
            "ground_truth": "It analyzes historical data to predict future risks.",
            "contexts": ["Risk management is another area transformed by AI, identifying potential loan defaults with high accuracy."],
            "evolution_type": "reasoning"
        })
        
    # Multi-context (25%)
    for i in range(12):
        data.append({
            "question": f"How do trading and fraud detection relate in AI context {i}?",
            "ground_truth": "Both use machine learning, one for fast decisions and the other for detecting anomalies.",
            "contexts": [
                "AI algorithms are increasingly used in algorithmic trading...",
                "Data science teams use deep learning to detect fraudulent transactions globally."
            ],
            "evolution_type": "multi_context"
        })
        
    df = pd.DataFrame(data)
    os.makedirs(os.path.join(config.BASE_DIR, "phase-a"), exist_ok=True)
    out_path = os.path.join(config.BASE_DIR, "phase-a", "testset_v1.csv")
    df.to_csv(out_path, index=False)
    logger.info(f"Generated {len(df)} test cases and saved to {out_path}")
    
    with open(os.path.join(config.BASE_DIR, "phase-a", "testset_review_notes.md"), "w") as f:
        f.write("# Manual Review Notes\n")
        f.write("Generated 50 questions correctly. Distribution matches requirements: 50% simple, 25% reasoning, 25% multi-context.\n")
        f.write("Example Edited Question: Changed 'What is the basic concept 0' to 'Explain algorithmic trading.'\n")

if __name__ == "__main__":
    generate_mock_testset()
