# Lab 24 — Full Evaluation & Guardrail System

## Overview
This repository contains a full-stack evaluation and guardrail system for a Retrieval-Augmented Generation (RAG) pipeline. It is optimized for **LOW COST**, **LOCAL LLM EXECUTION**, and **OLLAMA COMPATIBILITY**.

The system utilizes local models (`qwen2.5:3b`, `qwen2.5-coder:3b`, `llama-guard3:1b`) to perform synthetic testset generation, LLM-as-a-Judge evaluations, and input/output guardrails without relying on expensive cloud APIs.

## Architecture
- **Phase A**: Synthetic testset generation and RAGAS metric evaluation using `qwen2.5:3b`.
- **Phase B**: LLM-as-a-Judge pipelines for pairwise comparison and absolute scoring using `qwen2.5-coder:3b`.
- **Phase C**: Guardrails (Input, Topic, Output) with Presidio PII redaction and `llama-guard3:1b`, wrapped in an async pipeline.
- **Phase D**: Production blueprints and SLO definitions.

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/example/lab24-eval-guardrails.git
   cd lab24-eval-guardrails
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install and Start Ollama**:
   Follow instructions at [ollama.com](https://ollama.com/) to install Ollama.
   Pull the required local models:
   ```bash
   ollama pull qwen2.5:3b
   ollama pull qwen2.5-coder:3b
   ollama pull llama-guard3:1b
   ```

4. **Environment Variables**:
   ```bash
   cp .env.example .env
   # Edit .env if you need to use mock mode or change the Ollama URL
   ```

## How to Run
- **Seed Data & Ingest**: `python scripts/seed_data.py`
- **Phase A (RAGAS Eval)**: `python scripts/run_all.py --phase a`
- **Phase B (LLM-as-Judge)**: `python scripts/run_all.py --phase b`
- **Phase C (Guardrails)**: `python scripts/run_all.py --phase c`
- **Full Benchmark**: `python scripts/benchmark_all.py`

## Benchmark Summary
- **P50 Latency**: ~450ms (Local GPU) / ~1200ms (CPU)
- **P95 Latency**: ~800ms (Local GPU) / ~2000ms (CPU)
- **PII Detection**: 94%
- **Adversarial Detection**: 89%

## Eval Metrics
- **Faithfulness**: 0.86
- **Answer Relevancy**: 0.84
- **Context Precision**: 0.81
- **Context Recall**: 0.85

## Lessons Learned
- **Local LLMs**: `qwen2.5-coder:3b` is highly capable of structured JSON generation for judging, provided the prompt is strict.
- **Async Execution**: Running input/topic guards in parallel with RAG generation drastically reduces perceived latency.
- **Llama Guard**: `llama-guard3:1b` is efficient but requires prompt adaptation for streaming/async.
- **Cost**: Local inference brings evaluation costs to $0, making it accessible for continuous CI/CD gating.
