"""Turn each rendered PDF into page text.

Pages with a text layer are read directly. Scanned pages have no text, so they go
through OCR. We keep the method used for every page, because OCR text is less reliable
and that should show up in the results.
"""
import json
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from pypdf import PdfReader

PDF_DIR = Path("data/synthetic/pdfs")
OUT = Path("data/synthetic/document_pages.jsonl")
MIN_TEXT_CHARS = 40


def page_texts(path: Path) -> list[tuple[str, str]]:
    reader = PdfReader(path)
    texts = [p.extract_text() or "" for p in reader.pages]
    if all(len(t.strip()) >= MIN_TEXT_CHARS for t in texts):
        return [(t, "pdf_text") for t in texts]
    images = convert_from_path(path, dpi=300)
    return [(pytesseract.image_to_string(img, config="--psm 6"), "ocr") for img in images]


def main() -> None:
    docs = json.loads((PDF_DIR / "documents.json").read_text())
    n_pages = 0
    with OUT.open("w") as f:
        for d in docs:
            for i, (text, method) in enumerate(page_texts(PDF_DIR / d["path"]), start=1):
                f.write(json.dumps({"document_id": d["document_id"], "page": i,
                                    "text": text, "text_method": method}) + "\n")
                n_pages += 1
    print(f"wrote {n_pages} pages from {len(docs)} documents to {OUT}")


if __name__ == "__main__":
    main()
