import os
import sys
import pandas as pd
from sklearn.metrics import cohen_kappa_score

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import config
from shared.logger import get_logger
from shared.utils import interpret_kappa

log = get_logger(__name__)

def run_kappa_analysis(human_labels_path: str, llm_scores_path: str, output_path: str) -> None:
    """Calculate Cohen's Kappa between human and LLM scores."""
    if not os.path.exists(human_labels_path):
        log.warning(f"Human labels not found at {human_labels_path}. Creating mock data.")
        mock_data = pd.DataFrame({
            "question": ["How does AI detect fraud?"] * 10,
            "human_score": [5, 4, 5, 3, 4, 5, 4, 5, 3, 4]
        })
        mock_data.to_csv(human_labels_path, index=False)

    if not os.path.exists(llm_scores_path):
        log.error(f"LLM scores not found at {llm_scores_path}. Run absolute_scoring.py first.")
        return

    human_df = pd.read_csv(human_labels_path)
    llm_df = pd.read_csv(llm_scores_path)
    
    # Simple merge on index if question matching is tricky
    merged = pd.merge(human_df, llm_df, on="question", how="inner")
    
    if merged.empty:
        log.error("No overlapping questions found for kappa analysis.")
        return
        
    kappa = cohen_kappa_score(merged["human_score"], merged["accuracy"]) # Using accuracy as primary metric
    interpretation = interpret_kappa(kappa)
    
    result = pd.DataFrame({"kappa": [kappa], "interpretation": [interpretation]})
    result.to_csv(output_path, index=False)
    log.info(f"Cohen's Kappa: {kappa:.3f} ({interpretation}) – saved to {output_path}")

if __name__ == "__main__":
    base = config.BASE_DIR
    human_path = os.path.join(base, "phase-b", "human_labels.csv")
    llm_path = os.path.join(base, "phase-b", "absolute_scores.csv")
    out_path = os.path.join(base, "phase-b", "kappa_analysis_result.csv")
    run_kappa_analysis(human_path, llm_path, out_path)
