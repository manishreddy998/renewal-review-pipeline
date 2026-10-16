"""Download the public FSRA Ontario policy wording and record where it came from.

The PDF itself is not stored in git. We keep the URL and a checksum so anyone can
fetch the same file and confirm it has not changed.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import requests
from pypdf import PdfReader

SOURCES = [
    {
        "source_id": "fsra_oap1_en_2026_07",
        "title": "OAP 1 Ontario Automobile Policy, Owner's Policy (OAP1-EN.5, 07-2026)",
        "publisher": "Financial Services Regulatory Authority of Ontario",
        "url": "https://www.fsrao.ca/media/28946/download",
        "landing_page": "https://www.fsrao.ca/oap-1-ontario-automobile-policy-owners-policy",
        "expected_sha256": "a2c54ba6342e79190f449398daa313c30f6b9253c8846391c7ab329282566117",
    },
]

RAW_DIR = Path("data/raw/sources")


def fetch(source: dict, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / f"{source['source_id']}.pdf"
    if not pdf_path.exists():
        resp = requests.get(source["url"], timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        pdf_path.write_bytes(resp.content)

    data = pdf_path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != source["expected_sha256"]:
        print(f"warning: {source['source_id']} checksum changed, FSRA may have published a new version")

    reader = PdfReader(pdf_path)
    pages = [p.extract_text() or "" for p in reader.pages]
    text_path = out_dir / f"{source['source_id']}.pages.jsonl"
    with text_path.open("w") as f:
        for i, text in enumerate(pages, start=1):
            f.write(json.dumps({"source_id": source["source_id"], "page": i, "text": text}) + "\n")

    return {
        "source_id": source["source_id"],
        "title": source["title"],
        "publisher": source["publisher"],
        "url": source["url"],
        "sha256": sha,
        "page_count": len(pages),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    rows = [fetch(s, RAW_DIR) for s in SOURCES]
    (RAW_DIR / "manifest.json").write_text(json.dumps(rows, indent=2))
    for r in rows:
        print(f"{r['source_id']}: {r['page_count']} pages, sha256 {r['sha256'][:12]}")


if __name__ == "__main__":
    main()
