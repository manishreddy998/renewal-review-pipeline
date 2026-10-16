.PHONY: fetch synthetic load dbt smoke test check-databricks load-databricks dbt-databricks databricks

fetch:
	python -m renewal_review.fetch_sources

synthetic:
	python -m renewal_review.synthetic

load:
	python -m renewal_review.load_raw --target local

dbt:
	cd dbt && dbt build

test:
	pytest -q

smoke: test fetch synthetic load dbt

check-databricks:
	python -m renewal_review.databricks_check

load-databricks:
	python -m renewal_review.load_raw --target databricks

dbt-databricks:
	cd dbt && dbt build --target databricks

databricks: fetch synthetic check-databricks load-databricks dbt-databricks
