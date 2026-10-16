"""Build the raw table rows from local files, so Spark and Databricks load the same data."""
import json
from pathlib import Path

SOURCES_DIR = Path("data/raw/sources")
ANSWER_KEY = Path("data/synthetic/answer_key.jsonl")


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def policy_sources() -> list[dict]:
    rows = json.loads((SOURCES_DIR / "manifest.json").read_text())
    return [{k: r[k] for k in ("source_id", "title", "publisher", "url", "sha256", "page_count")} for r in rows]


def policy_source_pages() -> list[dict]:
    rows = []
    for path in sorted(SOURCES_DIR.glob("*.pages.jsonl")):
        rows += _jsonl(path)
    return rows


def policy_pairs() -> list[dict]:
    """One row per policy version, so prior and renewal sit side by side by pair_id."""
    rows = []
    for pair in _jsonl(ANSWER_KEY):
        for version in ("prior", "renewal"):
            p = pair[version]
            rows.append({
                "pair_id": pair["pair_id"],
                "agency_id": pair["agency_id"],
                "policy_version": version,
                "policy_number": p["policy_number"],
                "insured_name": p["insured_name"],
                "vehicle_year": p["vehicle_year"],
                "liability_limit": p["liability_limit"],
                "collision_deductible": p["collision_deductible"],
                "optional_coverages": ",".join(p["optional_coverages"]),
                "drivers": p["drivers"],
                "annual_premium": float(p["annual_premium"]),
                "planted_changes": ",".join(pair["planted_changes"]),
                "stamp": p["stamp"],
            })
    return rows


TABLES = {
    "policy_sources": (policy_sources, {
        "source_id": "string", "title": "string", "publisher": "string", "url": "string",
        "sha256": "string", "page_count": "int"}),
    "policy_source_pages": (policy_source_pages, {
        "source_id": "string", "page": "int", "text": "string"}),
    "policy_pairs": (policy_pairs, {
        "pair_id": "int", "agency_id": "string", "policy_version": "string",
        "policy_number": "string", "insured_name": "string", "vehicle_year": "int",
        "liability_limit": "bigint", "collision_deductible": "int", "optional_coverages": "string",
        "drivers": "int", "annual_premium": "double", "planted_changes": "string", "stamp": "string"}),
}
