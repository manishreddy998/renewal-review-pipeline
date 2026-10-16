import random

from pypdf import PdfReader
import io

from renewal_review import render
from renewal_review.synthetic import STAMP, generate


def test_every_page_carries_the_stamp(tmp_path, monkeypatch):
    monkeypatch.setattr(render, "OUT_DIR", tmp_path)
    monkeypatch.setattr(render, "SCAN_RATE", 0.0)
    rng = random.Random(0)
    for pair in generate(6, seed=5):
        for version in ("prior", "renewal"):
            name, _ = render.render(pair, version, rng)
            reader = PdfReader(io.BytesIO((tmp_path / name).read_bytes()))
            assert len(reader.pages) >= 2
            for page in reader.pages:
                assert STAMP in page.extract_text()
