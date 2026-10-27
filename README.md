# RAGAS Eval Framework

RAG app over `data/docs/` (LangChain + local Qdrant + OpenAI), scored against `datasets/golden_v1.jsonl` with RAGAS.

| Step | Command |
|---|---|
| Install | `pip install -r requirements.lock && pip install -e ".[dev]"` |
| Configure | Create `.env` with `OPENAI_API_KEY=...`; other settings in `src/rag_app/settings.py` are overridable by env var |
| Index docs | `python -m rag_app.ingest` (writes `.qdrant/`) |
| Ask one question | `python -m rag_app.query "What is the Business plan API rate limit?"` |
| Validate dataset | `python -m eval_framework.dataset datasets/golden_v1.jsonl` |
| Run evaluation | `python -m eval_framework.first_run [dataset.jsonl]` → per-row CSV in `evals/results/` |
| Gate a run | `python -m eval_framework.gate [run.csv]` → exit 1 if below `configs/thresholds.yaml` (default: latest run) |
| Lint + test | `ruff check src tests && pytest` (offline; no API key needed) |
| Regression | `pytest -m regression` — paid full run + gate; run manually (needs `OPENAI_API_KEY` and `python -m rag_app.ingest` first) |
| Dataset row | `{"id", "user_input", "reference", "source": "<file in data/docs> \| none", "tags": [...]}`; `source: "none"` marks out-of-scope rows, scored on factual correctness only |
