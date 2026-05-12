import argparse
import os
import sys
import subprocess

def run_command(cmd, cwd=None):
    # Set PYTHONPATH to the current directory to avoid ModuleNotFoundError
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    
    print(f"Executing: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True, cwd=cwd, env=env)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def run_phase_a():
    run_command("python phase-a/generate_testset.py")
    run_command("python phase-a/run_ragas_eval.py")
    run_command("python phase-a/analyze_failures.py")

def run_phase_b():
    run_command("python phase-b/judge_pipeline.py")
    run_command("python phase-b/absolute_scoring.py")
    run_command("python phase-b/kappa_analysis.py")
    run_command("python phase-b/bias_analysis.py")

def run_phase_c():
    run_command("python phase-c/full_pipeline.py")
    run_command("python phase-c/benchmark.py")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["a", "b", "c", "all", "pull"], default="all")
    args = parser.parse_args()
    
    if args.phase == "pull":
        print("--- PULLING REQUIRED MODELS ---")
        run_command("ollama pull qwen2.5:3b")
        run_command("ollama pull qwen2.5-coder:3b")
        run_command("ollama pull llama-guard3:1b")
        sys.exit(0)

    if args.phase in ["a", "all"]:
        print("--- RUNNING PHASE A ---")
        run_phase_a()
    if args.phase in ["b", "all"]:
        print("--- RUNNING PHASE B ---")
        run_phase_b()
    if args.phase in ["c", "all"]:
        print("--- RUNNING PHASE C ---")
        run_phase_c()
