from renewal_review.synthetic import AGENCIES, STAMP, generate


def test_pair_count_and_agencies():
    rows = generate(200, seed=1)
    assert len(rows) == 200
    assert {r["agency_id"] for r in rows} == {a["agency_id"] for a in AGENCIES}


def test_every_policy_is_stamped():
    for r in generate(50, seed=2):
        assert r["prior"]["stamp"] == STAMP
        assert r["renewal"]["stamp"] == STAMP


def test_same_seed_same_data():
    assert generate(20, seed=3) == generate(20, seed=3)


def test_large_increase_is_really_large():
    for r in generate(200, seed=4):
        if "premium_increase_large" in r["planted_changes"]:
            assert r["renewal"]["annual_premium"] > r["prior"]["annual_premium"] * 1.15
