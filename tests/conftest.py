import json
import os
from pathlib import Path

import pytest

# Settings require a key at construction; unit tests never hit the network.
# A real key (env or .env) is left alone so the regression run can use it.
if "OPENAI_API_KEY" not in os.environ and not Path(".env").exists():
    os.environ["OPENAI_API_KEY"] = "test-key"


@pytest.fixture
def write_jsonl(tmp_path):
    def _write(rows: list[dict | str]):
        path = tmp_path / "golden.jsonl"
        lines = [r if isinstance(r, str) else json.dumps(r) for r in rows]
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    return _write


@pytest.fixture
def docs_dir(tmp_path):
    d = tmp_path / "docs"
    d.mkdir()
    (d / "a.md").write_text("doc a", encoding="utf-8")
    return d
