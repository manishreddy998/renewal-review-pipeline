.PHONY: fetch synthetic dbt smoke test

fetch:
	python -m renewal_review.fetch_sources

synthetic:
	python -m renewal_review.synthetic

dbt:
	cd dbt && dbt build

test:
	pytest -q

smoke: test fetch synthetic dbt
