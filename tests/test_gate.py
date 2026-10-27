import pandas as pd
import pytest

from eval_framework.first_run import build_metrics
from eval_framework.gate import check, load_thresholds

pytestmark = pytest.mark.smoke

THRESHOLDS = {
    "overall": {"faithfulness": 0.8, "factual_correctness": 0.6},
    "by_tag": {"out-of-scope": {"factual_correctness": 0.8}},
    "max_error_rate": 0.25,
}


def results(**overrides):
    df = pd.DataFrame(
        {
            "id": ["a", "b", "c"],
            "tags": ["fact", "fact,numeric", "out-of-scope"],
            "faithfulness": [0.9, 0.9, None],
            "factual_correctness": [0.7, 0.7, 1.0],
        }
    )
    return df.assign(**overrides)


def test_passing_run_has_no_failures():
    assert check(results(), THRESHOLDS) == []


def test_overall_metric_below_minimum_fails():
    assert check(results(faithfulness=[0.5, 0.5, None]), THRESHOLDS) == [
        "overall faithfulness: 0.500 < 0.8"
    ]


def test_tag_metric_below_minimum_fails():
    failures = check(results(factual_correctness=[0.9, 0.9, 0.0]), THRESHOLDS)
    assert failures == ["tag out-of-scope factual_correctness: 0.000 < 0.8"]


def test_missing_metric_or_tag_fails():
    df = results(tags=["fact", "fact", "fact"]).drop(columns="faithfulness")
    assert check(df, THRESHOLDS) == [
        "overall faithfulness: nan < 0.8",
        "tag out-of-scope: no rows",
    ]


def test_error_rate_above_maximum_fails():
    df = results(
        faithfulness=[0.9, None, None],
        faithfulness_error=[None, "timeout", None],
        factual_correctness=[0.7, None, 1.0],
        factual_correctness_error=[None, "timeout", None],
    )
    assert check(df, THRESHOLDS) == ["error rate: 0.400 > 0.25"]


def test_committed_thresholds_cover_every_metric():
    thresholds = load_thresholds()
    assert set(thresholds["overall"]) == set(build_metrics())
    assert 0 <= thresholds["max_error_rate"] <= 1
