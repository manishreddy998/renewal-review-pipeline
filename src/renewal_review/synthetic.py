"""Synthetic policy pairs (last year and renewal) for three fake agencies.

This first version builds the structured answer key only. A later step renders each
record as a PDF with the stamp on every page. Because we plant the changes ourselves,
we know the right answer for every field and can measure extraction accuracy.
"""
import argparse
import json
import random
from datetime import date, timedelta
from pathlib import Path

STAMP = "SYNTHETIC TEST DATA, NOT A REAL POLICY"

AGENCIES = [
    {"agency_id": "AGY001", "name": "Maple Lane Insurance Brokers (fictional)"},
    {"agency_id": "AGY002", "name": "Lakeshore Risk Partners (fictional)"},
    {"agency_id": "AGY003", "name": "Northbay Family Insurance (fictional)"},
]

CARRIERS = ["Trillium Mutual (fictional)", "Huron General (fictional)", "Boreal Assurance (fictional)"]

VEHICLES = ["Honda Civic", "Toyota RAV4", "Ford F-150", "Hyundai Elantra", "Mazda CX-5",
            "Chevrolet Equinox", "Kia Sorento", "Subaru Outback", "Tesla Model 3", "Nissan Rogue"]

# Coverage names follow OAP 1 sections.
OPTIONAL_COVERAGES = ["collision_or_upset", "comprehensive", "specified_perils", "all_perils"]

# Changes a broker would care about at renewal, with how often we plant each one.
CHANGE_TYPES = {
    "premium_increase_large": 0.20,   # more than 15 percent
    "premium_increase_small": 0.30,
    "deductible_raised": 0.15,
    "liability_limit_lowered": 0.08,
    "coverage_dropped": 0.10,
    "driver_added": 0.10,
    "vehicle_changed": 0.07,
    "carrier_changed": 0.05,
}


def make_policy(rng: random.Random, agency_id: str, n: int) -> dict:
    coverages = sorted(rng.sample(OPTIONAL_COVERAGES, k=rng.randint(1, 2)))
    return {
        "policy_number": f"SYN-{agency_id}-{n:05d}",
        "agency_id": agency_id,
        "insured_name": f"Test Client {agency_id[-1]}{n:03d}",
        "carrier": rng.choice(CARRIERS),
        "effective_date": (date(2025, 1, 1) + timedelta(days=rng.randint(0, 364))).isoformat(),
        "vehicle": rng.choice(VEHICLES),
        "vehicle_year": rng.randint(2012, 2025),
        "liability_limit": rng.choice([1_000_000, 2_000_000]),
        "collision_deductible": rng.choice([500, 1000]),
        "optional_coverages": coverages,
        "drivers": rng.randint(1, 3),
        "annual_premium": round(rng.uniform(1400, 4200), 2),
        "stamp": STAMP,
    }


def make_renewal(rng: random.Random, prior: dict) -> tuple[dict, list[str]]:
    renewal = dict(prior, optional_coverages=list(prior["optional_coverages"]))
    prior_start = date.fromisoformat(prior["effective_date"])
    renewal["effective_date"] = prior_start.replace(year=prior_start.year + 1).isoformat()
    planted = [c for c, p in CHANGE_TYPES.items() if rng.random() < p]
    base_rise = rng.uniform(0.0, 0.05)
    premium = prior["annual_premium"] * (1 + base_rise)
    for change in planted:
        if change == "premium_increase_large":
            premium = prior["annual_premium"] * rng.uniform(1.16, 1.40)
        elif change == "premium_increase_small":
            premium = max(premium, prior["annual_premium"] * rng.uniform(1.05, 1.12))
        elif change == "deductible_raised":
            renewal["collision_deductible"] = prior["collision_deductible"] + 500
        elif change == "liability_limit_lowered" and prior["liability_limit"] > 1_000_000:
            renewal["liability_limit"] = 1_000_000
        elif change == "coverage_dropped" and renewal["optional_coverages"]:
            renewal["optional_coverages"].pop()
        elif change == "driver_added":
            renewal["drivers"] += 1
        elif change == "vehicle_changed":
            renewal["vehicle_year"] = min(2026, prior["vehicle_year"] + rng.randint(2, 6))
            renewal["vehicle"] = rng.choice([v for v in VEHICLES if v != prior["vehicle"]])
        elif change == "carrier_changed":
            renewal["carrier"] = rng.choice([c for c in CARRIERS if c != prior["carrier"]])
    renewal["annual_premium"] = round(premium, 2)
    return renewal, planted


def generate(pairs: int = 200, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    rows = []
    for i in range(pairs):
        agency = AGENCIES[i % len(AGENCIES)]
        prior = make_policy(rng, agency["agency_id"], i + 1)
        renewal, planted = make_renewal(rng, prior)
        rows.append({"pair_id": i + 1, "agency_id": agency["agency_id"],
                     "prior": prior, "renewal": renewal, "planted_changes": planted})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairs", type=int, default=200)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", default="data/synthetic/answer_key.jsonl")
    args = parser.parse_args()
    rows = generate(args.pairs, args.seed)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"wrote {len(rows)} pairs to {out}")


if __name__ == "__main__":
    main()
