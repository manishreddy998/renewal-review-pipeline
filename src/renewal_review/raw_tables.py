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
                "carrier": p["carrier"],
                "effective_date": p["effective_date"],
                "vehicle": p["vehicle"],
                "planted_changes": ",".join(pair["planted_changes"]),
                "stamp": p["stamp"],
            })
    return rows


def documents() -> list[dict]:
    rows = json.loads(Path("data/synthetic/pdfs/documents.json").read_text())
    return [{k: r[k] for k in ("document_id", "pair_id", "agency_id", "policy_version", "path", "scanned")}
            for r in rows]


def ams_policies() -> list[dict]:
    """Policy list as an agency management system would export it: number, agency, client.

    Agencies always know their own policy numbers, so we can use this list to repair
    policy numbers that OCR garbled.
    """
    seen = {}
    for pair in _jsonl(ANSWER_KEY):
        p = pair["prior"]
        seen[p["policy_number"]] = {"policy_number": p["policy_number"], "agency_id": pair["agency_id"],
                                    "insured_name": p["insured_name"]}
    return list(seen.values())


def document_pages() -> list[dict]:
    rows = _jsonl(Path("data/synthetic/document_pages.jsonl"))
    for r in rows:
        r["digit_words"] = json.dumps(r["digit_words"]) if r.get("digit_words") is not None else None
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
        "drivers": "int", "annual_premium": "double", "carrier": "string",
        "effective_date": "date", "vehicle": "string", "planted_changes": "string", "stamp": "string"}),
    "documents": (documents, {
        "document_id": "string", "pair_id": "int", "agency_id": "string", "policy_version": "string",
        "path": "string", "scanned": "boolean"}),
    "ams_policies": (ams_policies, {
        "policy_number": "string", "agency_id": "string", "insured_name": "string"}),
    "document_pages": (document_pages, {
        "document_id": "string", "page": "int", "text": "string", "text_method": "string",
        "digit_words": "string"}),
}
