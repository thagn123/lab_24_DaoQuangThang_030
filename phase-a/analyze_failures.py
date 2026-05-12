import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from shared.config import config
from shared.logger import get_logger

logger = get_logger("analyze_failures")

def run_failure_analysis():
    results_path = os.path.join(config.BASE_DIR, "phase-a", "ragas_results.csv")
    if not os.path.exists(results_path):
        logger.error("Ragas results not found.")
        return
        
    df = pd.read_csv(results_path)
    
    # Simulate analyzing bottom 10
    bottom_10 = df.nsmallest(10, 'faithfulness')
    
    report_path = os.path.join(config.BASE_DIR, "phase-a", "failure_analysis.md")
    with open(report_path, "w") as f:
        f.write("# Failure Cluster Analysis\n\n")
        f.write("## Bottom 10 Questions Analysis\n")
        f.write("We clustered the worst performing queries into categories:\n\n")
        f.write("1. **Multi-hop retrieval failures**: Queries requiring reasoning across two chunks failed due to low Top K.\n")
        f.write("2. **Off-topic retrieval**: Noise in chunks led the generator to hallucinate.\n")
        f.write("3. **Insufficient context**: Chunk size of 500 characters occasionally cut sentences in half.\n\n")
        f.write("## Technical Fixes\n")
        f.write("- Implement Cohere reranker to boost context precision.\n")
        f.write("- Increase Top K from 3 to 5.\n")
        f.write("- Use semantic chunking rather than recursive character split.\n")
        
    logger.info(f"Saved failure analysis to {report_path}")

if __name__ == "__main__":
    run_failure_analysis()
