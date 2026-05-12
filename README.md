# 🛡️ Lab 24 — Full Evaluation & Guardrail System

**Student:** Đào Quang Thắng — MSSV: 030  
**Repository:** https://github.com/thagn123/lab_24_DaoQuangThang_030  
**Submission Date:** 2026-05-12  

---

## 📌 Overview

This repository implements a **complete, production-style RAG Evaluation and Guardrail System** designed for:

- ✅ **Zero-cost** local LLM execution via Ollama
- ✅ **Full reproducibility** — no external APIs required
- ✅ **Async-ready** pipeline with P50/P95/P99 benchmarking
- ✅ **Multilingual PII detection** (Vietnamese + English)
- ✅ **Adversarial robustness** with 20 attack test cases

All models run **100% locally** via [Ollama](https://ollama.com/), eliminating API costs.

---

## 🏗️ Architecture

```
User Input
    │
    ▼
┌─────────────────────────────────┐
│      INPUT GUARDS (parallel)    │
│  PII Guard  │ Topic │ Injection │
└─────────────────────────────────┘
    │ (if all pass)
    ▼
┌─────────────────────────────────┐
│         RAG PIPELINE            │
│  Retriever (ChromaDB/FAISS)     │
│  Generator (qwen2.5:3b)         │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│      OUTPUT GUARD               │
│  llama-guard3:1b (safe/unsafe)  │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│      ASYNC AUDIT LOG            │
└─────────────────────────────────┘
    │
    ▼
  Response to User
```

---

## 🤖 Local Model Stack (Mandatory)

| Role | Model | Usage |
|------|-------|-------|
| Coding / Judge logic | `qwen2.5-coder:3b` | Phase B judging, reasoning |
| RAG generation / Eval | `qwen2.5:3b` | Phase A answers, Phase B scoring |
| Safety guard | `llama-guard3:1b` | Phase C output moderation |
| Embeddings | `nomic-embed-text` | Phase C topic guard (no GPU needed) |

---

## 📁 Repository Structure

```
lab24-eval-guardrails/
├── README.md
├── requirements.txt
├── prompts.md
├── .env.example
│
├── shared/                    # Shared utilities
│   ├── config.py              # Environment-based config
│   ├── logger.py              # Structured logging (loguru)
│   ├── ollama_client.py       # Async Ollama HTTP client + retries
│   ├── utils.py               # JSON parsing, CSV helpers
│   └── models.py              # Pydantic data models
│
├── rag/                       # RAG pipeline components
│   ├── ingest.py              # Document ingestion → ChromaDB
│   ├── retriever.py           # Async semantic retrieval
│   ├── generator.py           # LLM answer generation
│   └── pipeline.py            # End-to-end RAG pipeline
│
├── phase-a/                   # RAGAS Evaluation
│   ├── generate_testset.py    # 50 synthetic QA pairs
│   ├── run_ragas_eval.py      # RAGAS metric computation
│   ├── analyze_failures.py    # Failure clustering (KMeans)
│   ├── testset_v1.csv         # 50 generated QA pairs ✓
│   ├── ragas_results.csv      # Per-question metrics ✓
│   ├── ragas_summary.json     # Aggregated metrics ✓
│   ├── failure_analysis.md    # Root-cause analysis ✓
│   └── testset_review_notes.md
│
├── phase-b/                   # LLM-as-Judge
│   ├── judge_pipeline.py      # Pairwise comparison judge
│   ├── absolute_scoring.py    # Absolute 1-5 rubric scoring
│   ├── kappa_analysis.py      # Cohen's kappa computation
│   ├── bias_analysis.py       # Position/length bias charts
│   ├── pairwise_results.csv   # Judge pairwise decisions ✓
│   ├── absolute_scores.csv    # Per-question scores ✓
│   ├── human_labels.csv       # Human annotation baseline ✓
│   ├── judge_bias_report.md   # Bias analysis report ✓
│   └── charts/
│       └── position_bias.png  # Bias visualization ✓
│
├── phase-c/                   # Guardrail Stack
│   ├── input_guard.py         # Presidio PII + VN regex
│   ├── topic_guard.py         # Embedding-based topic filter
│   ├── injection_guard.py     # Prompt injection detection
│   ├── output_guard.py        # llama-guard3:1b safety check
│   ├── full_pipeline.py       # Async guarded RAG pipeline
│   ├── benchmark.py           # 100-request P50/P95/P99 bench
│   ├── attack_sets.py         # 20 adversarial attack payloads
│   ├── pii_test_results.csv   # PII detection results ✓
│   ├── adversarial_test_results.csv  # 20 attack results ✓
│   └── latency_benchmark.csv  # Latency with P50/P95/P99 ✓
│
├── phase-d/                   # Blueprint & Architecture
│   ├── blueprint.md           # SLOs, cost analysis, playbook
│   └── architecture.mmd       # Mermaid architecture diagram
│
├── scripts/
│   ├── run_all.py             # Master pipeline runner
│   ├── benchmark_all.py       # Full benchmark suite
│   └── seed_data.py           # Demo document ingestion
│
└── tests/
    ├── test_ragas.py
    ├── test_guards.py
    ├── test_pipeline.py
    └── test_judge.py
```

---

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Install Ollama: https://ollama.com/download
# Python 3.10+ required
```

### 2. Pull Required Local Models

```bash
ollama pull qwen2.5:3b
ollama pull qwen2.5-coder:3b
ollama pull llama-guard3:1b
ollama pull nomic-embed-text
```

Or use the convenience command:

```bash
python scripts/run_all.py --phase pull
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Default settings work out-of-the-box with local Ollama
```

Key settings in `.env`:

```dotenv
OLLAMA_BASE_URL=http://localhost:11434
MOCK_MODE=false          # Set true if Ollama unavailable
ENABLE_INPUT_GUARDS=true
ENABLE_OUTPUT_GUARDS=true
```

### 5. Seed Knowledge Base

```bash
python scripts/seed_data.py
```

### 6. Run Full Pipeline

```bash
# All phases
python scripts/run_all.py --phase all

# Individual phases
python scripts/run_all.py --phase a    # RAGAS evaluation
python scripts/run_all.py --phase b    # LLM-as-Judge
python scripts/run_all.py --phase c    # Guardrails + Benchmark
```

---

## 📊 Evaluation Results (Phase A — RAGAS)

Results from `phase-a/ragas_summary.json` — evaluated on 50 synthetic QA pairs:

| Metric | Score | Threshold | Status |
|--------|-------|-----------|--------|
| **Faithfulness** | **0.859** | ≥ 0.80 | ✅ PASS |
| **Answer Relevancy** | **0.785** | ≥ 0.80 | ⚠️ NEAR |
| **Context Precision** | **0.706** | ≥ 0.70 | ✅ PASS |
| **Context Recall** | **0.908** | ≥ 0.80 | ✅ PASS |

**Model used:** `qwen2.5:3b` via Ollama (local, $0 cost)  
**Testset types:** Simple / Reasoning / Multi-context (50 questions total)

### Failure Analysis Summary

- **Cluster 0 — Low Precision:** Retriever returns broad chunks; answers miss the specific sub-topic.
- **Cluster 1 — Low Relevancy:** Generator adds peripheral context not requested by the question.
- **Root cause:** `all-MiniLM-L6-v2` embedding distance is too coarse for domain-specific Vietnamese topics.

---

## ⚖️ LLM-as-Judge Results (Phase B)

### Absolute Scoring (qwen2.5-coder:3b as judge)

| Metric | Average Score (1–5) |
|--------|---------------------|
| Accuracy | **4.9 / 5** |
| Relevance | **4.0 / 5** |
| Conciseness | **3.0 / 5** |
| Helpfulness | **4.0 / 5** |

### Cohen's Kappa (LLM vs Human Agreement)

| Metric | Value |
|--------|-------|
| Cohen's κ | **0.72** |
| Interpretation | **Substantial agreement** |

### Bias Analysis

| Bias Type | Before Mitigation | After Swap-and-Average |
|-----------|-------------------|------------------------|
| Position A bias | 15% | < 2% |
| Length bias | moderate | reduced |

**Mitigation:** Swap-and-average — each pair judged twice (A→B, B→A) and scores averaged.

---

## 🛡️ Guardrail Results (Phase C)

### PII Detection (Input Guard)

| Entity Type | Detected | Accuracy |
|-------------|----------|----------|
| Email address | ✅ | 100% |
| VN Phone (09xx) | ✅ | 100% |
| CCCD (12 digits) | ✅ | 100% |
| Tax code | ✅ | 100% |

**Tool:** Microsoft Presidio + Vietnamese regex patterns

### Adversarial Robustness (20 attack tests)

| Attack Type | Tests | Blocked | Block Rate |
|-------------|-------|---------|------------|
| DAN attacks | 5 | 5 | **100%** |
| Jailbreak | 5 | 5 | **100%** |
| Payload split | 4 | 4 | **100%** |
| Encoding attacks | 3 | 3 | **100%** |
| Indirect injection | 3 | 3 | **100%** |
| **Total** | **20** | **20** | **100%** |

### Latency Benchmark (100 requests)

| Metric | Baseline (no guards) | Guarded Pipeline |
|--------|---------------------|-----------------|
| **P50** | 48.3 ms | **342 ms** |
| **P95** | 76.1 ms | **368 ms** |
| **P99** | 89.4 ms | **378 ms** |
| Overhead | — | ~294 ms |

> Guard overhead ≈ 294ms P50 — primarily from LLM output safety check (`llama-guard3:1b`)

---

## 💰 Cost Analysis

| Component | API Cost | Local Cost |
|-----------|----------|------------|
| RAG generation (1000 queries) | ~$2.50 (GPT-4o) | **$0** |
| Evaluation (RAGAS, 50 items) | ~$5.00 (OpenAI) | **$0** |
| Judge pipeline (200 calls) | ~$3.00 (GPT-4) | **$0** |
| Output guard (1000 checks) | ~$1.50 (Moderation API) | **$0** |
| **Total** | **~$12.00** | **$0** |

**Hardware requirement:** CPU-only (no GPU required). Tested on standard laptop.

---

## 🔧 Mock Mode (Offline Development)

If Ollama is not running, set `MOCK_MODE=true` in `.env`:

```dotenv
MOCK_MODE=true
```

All pipelines will generate **deterministic mock outputs** without crashing. This enables:
- CI/CD pipeline testing without Ollama
- Development on restricted machines
- Unit test execution

---

## 🧪 Running Tests

```bash
# Set PYTHONPATH first (required)
$env:PYTHONPATH = "."     # PowerShell
export PYTHONPATH=.       # Bash

pytest tests/ -v
```

---

## 📚 Lessons Learned

1. **Local LLMs are production-ready for evaluation tasks** — `qwen2.5-coder:3b` generates high-quality structured JSON for judging with strict prompt design.

2. **Async guards reduce perceived latency** — running PII, Topic, and Injection guards in parallel with `asyncio.gather()` adds only the cost of the slowest guard, not the sum.

3. **`triton` / `sentence-transformers` on Windows** — heavy PyTorch dependencies break on Windows without CUDA. Solution: use Ollama's native `nomic-embed-text` embedding API instead.

4. **Swap-and-average is critical** — without position swapping, LLM judges show 15% systematic position bias toward Answer A.

5. **llama-guard3:1b blocks all 20 adversarial attacks** — the 1B guard model is lightweight enough for production use while catching all tested jailbreak and injection attempts.

6. **Cost = $0** — complete evaluation pipeline runs at zero API cost using only local Ollama models.

---

## 📋 Submission Checklist

- [x] Phase A: 50 synthetic QA pairs generated (`testset_v1.csv`)
- [x] Phase A: RAGAS metrics computed (`ragas_results.csv`, `ragas_summary.json`)
- [x] Phase A: Failure analysis with clustering (`failure_analysis.md`)
- [x] Phase B: Pairwise judge pipeline (`pairwise_results.csv`)
- [x] Phase B: Absolute scoring rubric (`absolute_scores.csv`)
- [x] Phase B: Cohen's kappa analysis (`human_labels.csv`)
- [x] Phase B: Bias analysis chart (`charts/position_bias.png`)
- [x] Phase C: PII detection results (`pii_test_results.csv`)
- [x] Phase C: 20 adversarial tests (`adversarial_test_results.csv`)
- [x] Phase C: Latency benchmark P50/P95/P99 (`latency_benchmark.csv`)
- [x] Phase D: Blueprint with SLOs and cost analysis (`blueprint.md`)
- [x] Phase D: Architecture diagram (`architecture.mmd`)
- [x] `shared/ollama_client.py` with retries + mock mode
- [x] `requirements.txt` with pinned versions
- [x] `.env.example` configuration template
- [x] `prompts.md` prompt library
- [x] `tests/` unit test suite
- [x] GitHub repository pushed

---

## 🔗 Links

- **GitHub:** https://github.com/thagn123/lab_24_DaoQuangThang_030
- **Ollama:** https://ollama.com
- **RAGAS:** https://github.com/explodinggradients/ragas
- **Presidio:** https://microsoft.github.io/presidio/
