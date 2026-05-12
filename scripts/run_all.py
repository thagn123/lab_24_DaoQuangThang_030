"""
run_all.py - Master script to execute all Lab 24 pipeline phases.

Usage:
    python scripts/run_all.py --phase all     # Run all phases
    python scripts/run_all.py --phase a       # Run Phase A only
    python scripts/run_all.py --phase b       # Run Phase B only
    python scripts/run_all.py --phase c       # Run Phase C only
    python scripts/run_all.py --phase pull    # Pull all required Ollama models
"""
import argparse
import os
import sys
import subprocess


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_cmd(cmd: str, cwd: str = None) -> int:
    """Run a shell command with PYTHONPATH set to the repo root."""
    env = os.environ.copy()
    env["PYTHONPATH"] = BASE_DIR
    target_dir = cwd or BASE_DIR
    print(f"\n  ▶ {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=target_dir, env=env)
    if result.returncode != 0:
        print(f"  ✗ Command failed with exit code {result.returncode}")
    return result.returncode


def run_phase_a():
    print("\n━━━ PHASE A: RAGAS Evaluation ━━━")
    run_cmd("python phase-a/generate_testset.py")
    run_cmd("python phase-a/run_ragas_eval.py")
    run_cmd("python phase-a/analyze_failures.py")


def run_phase_b():
    print("\n━━━ PHASE B: LLM-as-Judge ━━━")
    run_cmd("python phase-b/judge_pipeline.py")
    run_cmd("python phase-b/absolute_scoring.py")
    run_cmd("python phase-b/kappa_analysis.py")
    run_cmd("python phase-b/bias_analysis.py")


def run_phase_c():
    print("\n━━━ PHASE C: Guardrails & Benchmark ━━━")
    run_cmd("python phase_c/full_pipeline.py")
    run_cmd("python phase_c/benchmark.py")


def pull_models():
    print("\n━━━ Pulling Required Ollama Models ━━━")
    for model in ["qwen2.5:3b", "qwen2.5-coder:3b", "llama-guard3:1b", "nomic-embed-text"]:
        print(f"\n  Pulling {model}...")
        run_cmd(f"ollama pull {model}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lab 24 Pipeline Runner")
    parser.add_argument(
        "--phase",
        choices=["a", "b", "c", "all", "pull"],
        default="all",
        help="Which phase to run (default: all)",
    )
    args = parser.parse_args()

    if args.phase == "pull":
        pull_models()
        sys.exit(0)

    if args.phase in ("a", "all"):
        run_phase_a()
    if args.phase in ("b", "all"):
        run_phase_b()
    if args.phase in ("c", "all"):
        run_phase_c()

    print("\n✓ All requested phases completed.")
