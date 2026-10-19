"""Stand-in policy wording for CI runs.

The FSRA site blocks requests from GitHub's runners, so CI cannot download the real
OAP 1 wording. This writes a short PDF that is clearly marked as a CI fixture, then
runs it through the same fetch() code, so the pages, manifest, load and dbt steps
are all tested. Local runs still use the real FSRA file through make fetch.
"""
import io
import json

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from renewal_review.fetch_sources import RAW_DIR, fetch

SOURCE = {
    "source_id": "ci_fixture_wording",
    "title": "CI fixture policy wording (not a real policy)",
    "publisher": "renewal-review-pipeline CI",
    "url": "about:ci-fixture",
    "landing_page": "about:ci-fixture",
    "expected_sha256": "c4e02e8be24b845d78d68411ec807bb1e42ed82f66e01243f8db1a90bbc3ca23",
}

PAGES = [
    "CI FIXTURE, NOT A REAL POLICY. Section 1: Liability coverage applies to bodily injury and property damage.",
    "CI FIXTURE, NOT A REAL POLICY. Section 2: Collision coverage pays for damage to the described automobile.",
]


def build_pdf() -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, invariant=1)
    for text in PAGES:
        c.drawString(72, 720, text)
        c.showPage()
    c.save()
    return buf.getvalue()


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / f"{SOURCE['source_id']}.pdf").write_bytes(build_pdf())
    row = fetch(SOURCE, RAW_DIR)
    assert row["page_count"] == len(PAGES)
    (RAW_DIR / "manifest.json").write_text(json.dumps([row], indent=2))
    print(f"{row['source_id']}: {row['page_count']} pages, sha256 {row['sha256'][:12]}")


if __name__ == "__main__":
    main()
