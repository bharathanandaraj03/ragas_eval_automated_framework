import asyncio

import pandas as pd
import pytest

from eval_framework.first_run import run
from eval_framework.gate import check, load_thresholds
from rag_app.settings import get_settings

pytestmark = pytest.mark.regression


def test_golden_set_meets_thresholds():
    """Full paid run: answers every golden question and scores it with the judge model."""
    if get_settings().openai_api_key == "test-key":
        pytest.skip("needs a real OPENAI_API_KEY")
    out = asyncio.run(run("datasets/golden_v1.jsonl"))
    failures = check(pd.read_csv(out), load_thresholds())
    assert not failures, "\n".join(failures)
