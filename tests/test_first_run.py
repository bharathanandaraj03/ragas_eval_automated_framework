import asyncio
from types import SimpleNamespace

import pytest

from eval_framework.dataset import GoldenRow
from eval_framework.first_run import build_metrics, metric_inputs, score_row
from rag_app.query import RagResponse

pytestmark = pytest.mark.smoke

METRICS = {
    "faithfulness",
    "answer_relevancy",
    "context_precision",
    "context_recall",
    "factual_correctness",
}


def golden(source="a.md"):
    return GoldenRow(id="r1", user_input="What is X?", reference="X.", source=source, tags=["fact"])


def rag():
    return RagResponse(question="What is X?", answer="X.", contexts=["ctx"], sources=["a.md"])


def test_build_metrics_has_each_metric_once():
    assert set(build_metrics()) == METRICS


def test_in_scope_row_feeds_every_metric():
    assert set(metric_inputs(golden(), rag())) == METRICS


def test_out_of_scope_row_only_checks_refusal():
    assert metric_inputs(golden(source="none"), rag()) == {
        "factual_correctness": {"response": "X.", "reference": "X."}
    }


class FakeMetric:
    def __init__(self, value=None, error=None):
        self.value, self.error = value, error

    async def ascore(self, **kwargs):
        if self.error:
            raise self.error
        return SimpleNamespace(value=self.value)


def test_score_row_records_scores_and_isolates_failures():
    metrics = {name: FakeMetric(value=1.0) for name in METRICS}
    metrics["context_recall"] = FakeMetric(error=RuntimeError("rate limited"))

    record = asyncio.run(score_row(metrics, golden(), rag(), asyncio.Semaphore(2)))

    assert record["faithfulness"] == 1.0
    assert record["context_recall"] is None
    assert record["context_recall_error"] == "rate limited"
    assert record["tags"] == "fact"
