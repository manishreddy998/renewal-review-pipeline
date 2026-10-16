"""Render each synthetic policy as a stamped PDF declarations document.

Each agency uses its own layout and its own labels, the way real carriers and brokers do.
About one in seven documents is turned into a scanned looking image PDF (slight rotation,
grey noise, no text layer), so the extraction step has to deal with OCR too.
"""
import argparse
import io
import json
import random
from pathlib import Path

from PIL import Image, ImageFilter
from pdf2image import convert_from_bytes
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from renewal_review.synthetic import STAMP

OUT_DIR = Path("data/synthetic/pdfs")
SCAN_RATE = 0.15
W, H = letter

COVERAGE_LABELS = {
    "AGY001": {"collision_or_upset": "Collision or Upset", "comprehensive": "Comprehensive",
               "specified_perils": "Specified Perils", "all_perils": "All Perils"},
    "AGY002": {"collision_or_upset": "COLLISION/UPSET (Sec. 7.3)", "comprehensive": "COMPREHENSIVE (Sec. 7.4)",
               "specified_perils": "SPECIFIED PERILS (Sec. 7.5)", "all_perils": "ALL PERILS (Sec. 7.2)"},
    "AGY003": {"collision_or_upset": "collision / upset", "comprehensive": "comprehensive cover",
               "specified_perils": "specified perils", "all_perils": "all perils"},
}


def stamp(c: canvas.Canvas, page: int, pages: int) -> None:
    c.setFont("Helvetica-Bold", 9)
    c.setFillGray(0.35)
    c.drawCentredString(W / 2, H - 22, STAMP)
    c.drawCentredString(W / 2, 18, f"{STAMP}  |  page {page} of {pages}")
    c.saveState()
    c.setFont("Helvetica-Bold", 40)
    c.setFillGray(0.9)
    c.translate(W / 2, H / 2)
    c.rotate(35)
    c.drawCentredString(0, 0, "SYNTHETIC TEST DATA")
    c.restoreState()
    c.setFillGray(0)


def money(agency: str, v: float) -> str:
    if agency == "AGY001":
        return f"${v:,.2f}"
    if agency == "AGY002":
        return f"{v:.2f} CAD"
    return f"$ {v:,.0f}" if float(v).is_integer() else f"$ {v:,.2f}"


def layout_table(c, p, agency, version):
    """AGY001: clean two column table."""
    stamp(c, 1, 2)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(60, H - 70, "Maple Lane Insurance Brokers (fictional)")
    c.setFont("Helvetica", 11)
    c.drawString(60, H - 90, f"Automobile Declarations, {'Renewal' if version == 'renewal' else 'Current Term'}")
    rows = [("Policy Number", p["policy_number"]), ("Named Insured", p["insured_name"]),
            ("Insurer", p["carrier"]), ("Effective Date", p["effective_date"]),
            ("Vehicle", f"{p['vehicle_year']} {p['vehicle']}"), ("Listed Drivers", str(p["drivers"]))]
    y = H - 140
    for k, v in rows:
        c.drawString(70, y, k)
        c.drawString(260, y, v)
        y -= 22
    c.showPage()
    stamp(c, 2, 2)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(60, H - 70, "Coverages (Ontario Automobile Policy OAP 1)")
    c.setFont("Helvetica", 11)
    y = H - 110
    lines = [("Third Party Liability", money(agency, p["liability_limit"]).replace(".00", "")),
             ("Accident Benefits", "Standard"), ("Direct Compensation Property Damage", "Included")]
    for cov in p["optional_coverages"]:
        ded = p["collision_deductible"] if cov == "collision_or_upset" else 500
        lines.append((COVERAGE_LABELS[agency][cov], f"Deductible {money(agency, ded).replace('.00', '')}"))
    if "collision_or_upset" not in p["optional_coverages"]:
        lines.append(("Collision Deductible (if added)", money(agency, p["collision_deductible"]).replace(".00", "")))
    for k, v in lines:
        c.drawString(70, y, k)
        c.drawString(330, y, v)
        y -= 22
    c.setFont("Helvetica-Bold", 12)
    c.drawString(70, y - 20, "Total Annual Premium")
    c.drawString(330, y - 20, money(agency, p["annual_premium"]))


def layout_caps(c, p, agency, version):
    """AGY002: all caps carrier style form with section codes."""
    stamp(c, 1, 3)
    c.setFont("Courier-Bold", 14)
    c.drawString(50, H - 70, "LAKESHORE RISK PARTNERS (FICTIONAL)")
    c.setFont("Courier", 10)
    c.drawString(50, H - 88, "CERTIFICATE / DECLARATION PAGE" + ("  ** RENEWAL **" if version == "renewal" else ""))
    c.drawString(50, H - 120, f"POL NO.......: {p['policy_number']}")
    c.drawString(50, H - 136, f"INSURED......: {p['insured_name'].upper()}")
    c.drawString(50, H - 152, f"COMPANY......: {p['carrier'].upper()}")
    c.drawString(50, H - 168, f"TERM BEGINS..: {p['effective_date']}")
    c.showPage()
    stamp(c, 2, 3)
    c.setFont("Courier", 10)
    c.drawString(50, H - 70, "DESCRIBED AUTOMOBILE")
    c.drawString(50, H - 90, f"  YR/MAKE/MODEL: {p['vehicle_year']} {p['vehicle'].upper()}")
    c.drawString(50, H - 106, f"  NO. OF OPERATORS: {p['drivers']}")
    c.showPage()
    stamp(c, 3, 3)
    c.setFont("Courier", 10)
    c.drawString(50, H - 70, "COVERAGE SCHEDULE")
    y = H - 92
    c.drawString(50, y, f"  SEC 3 LIABILITY LIMIT ........ {p['liability_limit']:.2f} CAD"); y -= 16
    c.drawString(50, y, f"  COLLISION DEDUCTIBLE ......... {p['collision_deductible']:.2f} CAD"); y -= 16
    for cov in p["optional_coverages"]:
        c.drawString(50, y, f"  {COVERAGE_LABELS[agency][cov]} ... INCLUDED"); y -= 16
    c.drawString(50, y - 10, f"  TOTAL PREMIUM (12 MOS) ....... {money(agency, p['annual_premium'])}")


def layout_letter(c, p, agency, version):
    """AGY003: friendly letter with the facts inside sentences."""
    stamp(c, 1, 2)
    c.setFont("Times-Bold", 15)
    c.drawString(60, H - 70, "Northbay Family Insurance (fictional)")
    c.setFont("Times-Roman", 11)
    word = "renewal offer" if version == "renewal" else "policy summary"
    text = [
        f"Dear {p['insured_name']},",
        "",
        f"Here is your {word} for policy {p['policy_number']}, placed with {p['carrier']}.",
        f"Coverage starts on {p['effective_date']} and runs for twelve months.",
        f"It covers your {p['vehicle_year']} {p['vehicle']}, with {p['drivers']} driver(s) listed.",
    ]
    y = H - 110
    for line in text:
        c.drawString(60, y, line)
        y -= 18
    c.showPage()
    stamp(c, 2, 2)
    c.setFont("Times-Roman", 11)
    covs = ", ".join(COVERAGE_LABELS[agency][x] for x in p["optional_coverages"]) or "none"
    text = [
        f"Your liability protection is {money(agency, p['liability_limit'])}.",
        f"Optional coverages on this policy: {covs}.",
        f"Your collision deductible is {money(agency, p['collision_deductible'])}.",
        "",
        f"The total yearly premium is {money(agency, p['annual_premium'])}.",
        "",
        "Thank you for choosing a fictional brokerage for testing.",
    ]
    y = H - 80
    for line in text:
        c.drawString(60, y, line)
        y -= 18


LAYOUTS = {"AGY001": layout_table, "AGY002": layout_caps, "AGY003": layout_letter}


def scan_look(pdf_bytes: bytes, rng: random.Random) -> bytes:
    pages = convert_from_bytes(pdf_bytes, dpi=150)
    out = []
    for img in pages:
        img = img.convert("L").rotate(rng.uniform(-1.5, 1.5), expand=False, fillcolor=255)
        noise = Image.effect_noise(img.size, 22).convert("L")
        img = Image.blend(img, noise, 0.12).filter(ImageFilter.GaussianBlur(0.6))
        out.append(img.convert("RGB"))
    buf = io.BytesIO()
    out[0].save(buf, format="PDF", save_all=True, append_images=out[1:], resolution=150)
    return buf.getvalue()


def render(pair: dict, version: str, rng: random.Random) -> tuple[str, bool]:
    p = pair[version]
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setTitle(f"{p['policy_number']} {version} {STAMP}")
    LAYOUTS[pair["agency_id"]](c, p, pair["agency_id"], version)
    c.showPage()
    c.save()
    data = buf.getvalue()
    scanned = rng.random() < SCAN_RATE
    if scanned:
        data = scan_look(data, rng)
    name = f"{pair['agency_id']}/{p['policy_number']}_{version}.pdf"
    path = OUT_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return name, scanned


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--answer-key", default="data/synthetic/answer_key.jsonl")
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    docs = []
    for line in Path(args.answer_key).read_text().splitlines():
        pair = json.loads(line)
        for version in ("prior", "renewal"):
            name, scanned = render(pair, version, rng)
            docs.append({"document_id": name.rsplit("/", 1)[1][:-4], "pair_id": pair["pair_id"],
                         "agency_id": pair["agency_id"], "policy_version": version,
                         "path": name, "scanned": scanned})
    (OUT_DIR / "documents.json").write_text(json.dumps(docs, indent=1))
    print(f"rendered {len(docs)} documents, {sum(d['scanned'] for d in docs)} scanned look")


if __name__ == "__main__":
    main()
