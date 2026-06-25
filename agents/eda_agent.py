import csv
import os
from typing import Dict, Any

class EDAGent:
    """Lightweight EDA agent that reads a CSV without pandas.
    It provides basic statistics required for tests: sets `eda_success` to True
    and attaches an `eda` dict with row/column counts.
    """

    def __init__(self, data_dir: str = None):
        # If a specific data directory is provided (e.g., the API's DATA_DIR), use it.
        # Otherwise fall back to the project‑root‑relative "data" folder.
        self.data_dir = data_dir or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "data")
        )

    def _load_csv(self, dataset_id: str) -> list:
        file_path = os.path.join(self.data_dir, f"{dataset_id}.csv")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset {dataset_id} not found at {file_path}")
        with open(file_path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            return [row for row in reader]

    def run(self, dataset_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        rows = self._load_csv(dataset_id)
        # Basic stats
        stats = {
            "rows": len(rows),
            "columns": len(rows[0]) if rows else 0,
            "column_stats": {}
        }
        if rows:
            for col in rows[0].keys():
                col_vals = [row[col] for row in rows]
                missing = sum(1 for v in col_vals if v == "" or v is None)
                unique = len(set(col_vals))
                stats["column_stats"][col] = {"missing": missing, "unique": unique}
        context["eda"] = stats
        context["eda_success"] = True
        return context
