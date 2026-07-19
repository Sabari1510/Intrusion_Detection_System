"""Small helpers."""

import csv
import io
from config import FEATURES


def rows_from_csv(content: bytes) -> list[dict]:
    """Parse CSV bytes into list of feature dicts."""
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for row in reader:
        rows.append({k: float(v) for k, v in row.items() if k in FEATURES or k})
    return rows
