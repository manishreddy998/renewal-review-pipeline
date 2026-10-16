"""Pull the result tables from Databricks into results/ as CSV files.

The dashboard and the summary read these files, so they work without a Databricks login.
"""
import csv
import os
from pathlib import Path

from renewal_review.query import run

CATALOG = os.environ.get("DATABRICKS_CATALOG", "workspace")
SCHEMA = "renewal_review"
OUT = Path("results")

TABLES = {
    "renewal_queue": "select * from {s}.mart_renewal_queue order by agency_id, agency_rank",
    "change_evidence": "select * from {s}.fct_change_evidence order by agency_id, pair_id, change_type",
    "field_accuracy": "select * from {s}.eval_field_accuracy order by field, agency_id, document_type",
    "field_errors": "select * from {s}.eval_field_errors order by field, document_id",
    "change_detection": "select * from {s}.eval_change_detection",
    "queue_agreement": "select * from {s}.eval_queue_agreement",
    "data_checks": "select * from {s}.eval_data_checks",
    "cost": "select * from {s}.eval_cost",
}


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name, sql in TABLES.items():
        cols, rows = run(sql.format(s=f"{CATALOG}.{SCHEMA}"))
        with (OUT / f"{name}.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(cols)
            w.writerows(rows)
        print(f"results/{name}.csv: {len(rows)} rows")


if __name__ == "__main__":
    main()
