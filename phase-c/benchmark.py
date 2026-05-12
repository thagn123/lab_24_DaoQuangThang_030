import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import time
import numpy as np
import pandas as pd
from full_pipeline import FullGuardedPipeline
from shared.config import config
from shared.logger import get_logger

logger = get_logger("benchmark")

async def run_benchmark():
    pipeline = FullGuardedPipeline()
    queries = ["How does AI predict stock prices?"] * 100
    
    latencies = []
    
    logger.info("Starting latency benchmark of 100 queries...")
    for i, q in enumerate(queries):
        start = time.time()
        res = await pipeline.ainvoke(q)
        latency = (time.time() - start) * 1000
        latencies.append(latency)
        if (i+1) % 10 == 0:
            logger.info(f"Processed {i+1}/100 queries.")
            
    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)
    p99 = np.percentile(latencies, 99)
    
    logger.info(f"Benchmark complete. P50: {p50:.2f}ms, P95: {p95:.2f}ms, P99: {p99:.2f}ms")
    
    df = pd.DataFrame({"query_idx": range(100), "latency_ms": latencies})
    os.makedirs(config.OUTPUTS_DIR, exist_ok=True)
    out_path = os.path.join(config.OUTPUTS_DIR, "latency_benchmark.csv")
    df.to_csv(out_path, index=False)
    logger.info(f"Saved benchmark results to {out_path}")
    
if __name__ == "__main__":
    asyncio.run(run_benchmark())
