"""Load coded excerpts from CSV (or JSON) into plain Python records.

Expected CSV columns: excerpt_id, excerpt, coder_a, coder_b
Extra columns are ignored; blank coder labels raise ValueError.
"""
import csv
import json
from pathlib import Path

__all__ = ["load_csv", "load_json", "load_coding_file"]

REQUIRED = ("excerpt_id", "excerpt", "coder_a", "coder_b")


def load_csv(path):
    path = Path(path)
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{path}: missing columns {missing}")
        rows = []
        for i, row in enumerate(reader, start=2):
            rec = {c: (row.get(c) or "").strip() for c in REQUIRED}
            if not rec["coder_a"] or not rec["coder_b"]:
                raise ValueError(f"{path}:{i}: blank coder label")
            rows.append(rec)
    if not rows:
        raise ValueError(f"{path}: no data rows")
    return rows


def load_json(path):
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError(f"{path}: expected a non-empty JSON list")
    rows = []
    for i, item in enumerate(data):
        missing = [c for c in REQUIRED if c not in item]
        if missing:
            raise ValueError(f"{path}[{i}]: missing keys {missing}")
        rows.append({c: str(item[c]).strip() for c in REQUIRED})
    return rows


def load_coding_file(path):
    path = Path(path)
    if path.suffix.lower() == ".json":
        return load_json(path)
    if path.suffix.lower() == ".csv":
        return load_csv(path)
    raise ValueError(f"unsupported file type: {path.suffix} (use .csv or .json)")


def labels(rows):
    """Return (coder_a_labels, coder_b_labels) from loaded rows."""
    return [r["coder_a"] for r in rows], [r["coder_b"] for r in rows]
