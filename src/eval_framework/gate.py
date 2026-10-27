"""Fail an eval run whose scores fall below configs/thresholds.yaml."""

import argparse
import sys
from pathlib import Path

import pandas as pd
import yaml

THRESHOLDS = Path("configs/thresholds.yaml")
RESULTS_DIR = Path("evals/results")


def load_thresholds(path: str | Path = THRESHOLDS) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def _below(scores: pd.DataFrame, minimums: dict[str, float], label: str) -> list[str]:
    failures = []
    for metric, minimum in minimums.items():
        mean = float(scores[metric].mean()) if metric in scores else float("nan")
        if pd.isna(mean) or mean < minimum:
            failures.append(f"{label} {metric}: {mean:.3f} < {minimum}")
    return failures


def check(df: pd.DataFrame, thresholds: dict) -> list[str]:
    """Return one message per breached threshold; empty means the run passes."""
    overall = thresholds.get("overall", {})
    failures = _below(df, overall, "overall")

    tagged = df.assign(tags=df["tags"].fillna("").str.split(",")).explode("tags")
    for tag, minimums in thresholds.get("by_tag", {}).items():
        rows = tagged[tagged["tags"] == tag]
        if rows.empty:
            failures.append(f"tag {tag}: no rows")
        else:
            failures += _below(rows, minimums, f"tag {tag}")

    max_error_rate = thresholds.get("max_error_rate")
    if max_error_rate is not None:
        errors = int(df[[c for c in df if c.endswith("_error")]].notna().sum().sum())
        scored = int(df[[m for m in overall if m in df]].notna().sum().sum())
        rate = errors / (errors + scored) if errors + scored else 0.0
        if rate > max_error_rate:
            failures.append(f"error rate: {rate:.3f} > {max_error_rate}")
    return failures


def latest_results() -> Path:
    runs = sorted(RESULTS_DIR.glob("run_*.csv"))
    if not runs:
        raise SystemExit(f"no runs in {RESULTS_DIR}")
    return runs[-1]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", nargs="?", type=Path, help="run CSV (default: latest)")
    parser.add_argument("--thresholds", type=Path, default=THRESHOLDS)
    args = parser.parse_args()

    results = args.results or latest_results()
    failures = check(pd.read_csv(results), load_thresholds(args.thresholds))
    print(f"{results}: " + ("FAIL\n  " + "\n  ".join(failures) if failures else "PASS"))
    sys.exit(1 if failures else 0)
