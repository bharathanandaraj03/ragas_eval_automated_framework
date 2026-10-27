import pytest

from eval_framework.dataset import load_golden

pytestmark = pytest.mark.smoke


def row(id_="r1", source="a.md", **kw):
    return {"id": id_, "user_input": "What is X?", "reference": "X.", "source": source, **kw}


def test_loads_valid_rows_and_skips_blank_lines(write_jsonl, docs_dir):
    path = write_jsonl([row("r1"), "", row("r2", source="none", tags=["out-of-scope"])])
    rows = load_golden(path, docs_dir)
    assert [r.id for r in rows] == ["r1", "r2"]
    assert rows[1].tags == ["out-of-scope"]


def test_duplicate_id_is_reported_as_duplicate(write_jsonl, docs_dir):
    path = write_jsonl([row("r1"), row("r1")])
    with pytest.raises(ValueError, match=r"line 2: duplicate id 'r1'"):
        load_golden(path, docs_dir)


def test_missing_source_file_is_reported(write_jsonl, docs_dir):
    path = write_jsonl([row("r1", source="missing.md")])
    with pytest.raises(ValueError, match=r"line 1: source file missing.md not found"):
        load_golden(path, docs_dir)


def test_schema_error_includes_line_number(write_jsonl, docs_dir):
    path = write_jsonl([row("r1"), row("r2", user_input="hi")])
    with pytest.raises(ValueError, match=r"^line 2:"):
        load_golden(path, docs_dir)


def test_committed_golden_dataset_is_valid():
    rows = load_golden("datasets/golden_v1.jsonl")
    assert len(rows) == 30
