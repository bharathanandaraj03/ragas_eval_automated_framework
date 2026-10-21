"""Step 4: run the RAG app over the golden set and score it with RAGAS."""
import asyncio
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from openai import AsyncOpenAI, OpenAIEm
from ragas.embeddings.openai_provider import OpenAIEmbeddings
from ragas.llms.base import llm_factory
from ragas.metrics.collections import(
    AnswerRelevancy,
    ContextPrecisionWithReference,
    ContextRecall,
    FactualCorrectness,
    Faithfulness,
)

from eval_framework.dataset import GoldenRow, load_golden
from rag_app.query import RagPipeline, RagResponse
from rag_app.settings import get_settings

MAX_CONCURRENCY = 8 
# parallel judge calls; lower it if you see rate-limit errors
RESULTS_DIR = Path("evals/results")

def build_metrics() -> dict:
    s = get_settings()
    client = AsyncOpenAI(api_key=s.openai_api_key,timeout=60,max_retries=3)
    llm = llm_factory(s.judge_model,client=client)
    embeddings = OpenAIEmbeddings(client=client,model=s.embedding_model)

    return{
        "faithfulness": Faithfulness(llm=llm),
        "faithfulness": Faithfulness(llm=llm),
        "answer_relevancy": AnswerRelevancy(llm=llm, embeddings=embeddings),
        "context_precision": ContextPrecisionWithReference(llm=llm),
        "context_recall": ContextRecall(llm=llm),
        "factual_correctness": FactualCorrectness(llm=llm),
    }

def metric_inputs(row: GoldenRow, rag: RagResponse) -> dict[str, dict]:
    """Map each metric to only the fields it needs."""
    q, ans, ctx, ref = row.user_input, rag.answer, rag.contexts, row.reference
    if row.source == "none":
        # Out-of-scope: nothing relevant exists to retrieve, so only check the refusal.
        return {"factual_correctness": dict(response=ans, reference=ref)}
    return {
        "faithfulness": dict(user_input=q, response=ans, retrieved_contexts=ctx),
        "answer_relevancy": dict(user_input=q, response=ans),
        "context_precision": dict(user_input=q, reference=ref, retrieved_contexts=ctx),
        "context_recall": dict(user_input=q, retrieved_contexts=ctx, reference=ref),
        "factual_correctness": dict(response=ans, reference=ref),
    }


async def score_row(metrics: dict, row: GoldenRow, rag: RagResponse, sem: asyncio.Semaphore) -> dict:
    record = {
        "id": row.id,
        "tags": ",".join(row.tags),
        "user_input": row.user_input,
        "response": rag.answer,
        "reference": row.reference,
        "sources": ";".join(rag.sources),
    }

    async def one(name: str, kwargs: dict):
        async with sem:
            try:
                return name, (await metrics[name].ascore(**kwargs)).value
            except Exception as exc:  # one failed judge call must not kill the run
                record[f"{name}_error"] = str(exc)[:200]
                return name, None

    results = await asyncio.gather(*(one(n, kw) for n, kw in metric_inputs(row, rag).items()))
    record.update(dict(results))
    return record


async def run(dataset_path: str) -> Path:
    rows = load_golden(dataset_path)
    pipeline = RagPipeline()
    print(f"Answering {len(rows)} questions...")
    answers = [pipeline.answer(r.user_input) for r in rows]

    metrics = build_metrics()
    sem = asyncio.Semaphore(MAX_CONCURRENCY)
    print("Scoring...")
    records = await asyncio.gather(*(score_row(metrics, r, a, sem) for r, a in zip(rows, answers)))

    df = pd.DataFrame(records)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"run_{datetime.now():%Y%m%d_%H%M%S}.csv"
    df.to_csv(out, index=False, encoding="utf-8")

    cols = [c for c in metrics if c in df]
    print("\nOverall mean:\n" + df[cols].mean().round(3).to_string())
    by_tag = df.assign(tags=df["tags"].str.split(",")).explode("tags").groupby("tags")[cols].mean()
    print("\nBy tag:\n" + by_tag.round(2).to_string())
    print(f"\nPer-row scores: {out}")
    return out


if __name__ == "__main__":
    asyncio.run(run(sys.argv[1] if len(sys.argv) > 1 else "datasets/golden_v1.jsonl"))