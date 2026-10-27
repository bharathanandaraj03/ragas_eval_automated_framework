""" Load and validate the golden dataset."""

import sys
from collections import Counter
from pathlib import Path

from pydantic import BaseModel, Field

DOCS_DIR = Path("data/docs")

class GoldenRow(BaseModel):
    id: str
    user_input: str = Field(min_length=5)
    reference: str = Field(min_length=1)
    source: str
    tags: list[str] = []

def load_golden(path: str | Path, docs_dir: str | Path = DOCS_DIR) -> list[GoldenRow]:
    rows: list[GoldenRow] = []
    seen: set[str] = set()
    for line_no, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(),1):
        if not line.strip():
            continue
        try:
            row = GoldenRow.model_validate_json(line)
        except ValueError as exc:
            raise ValueError(f"line {line_no}: {exc}") from exc
        if row.id in seen:
            raise ValueError(f"line {line_no}: duplicate id {row.id!r}")
        if row.source != "none" and not (Path(docs_dir) / row.source).is_file():
            raise ValueError(f"line {line_no}: source file {row.source} not found")
        seen.add(row.id)
        rows.append(row)
    return rows
        
if __name__ == "__main__":
    rows = load_golden(sys.argv[1])
    tags = Counter(t for r in rows for t in r.tags)
    print(f"{len(rows)} rows; tags: {dict(tags)}")