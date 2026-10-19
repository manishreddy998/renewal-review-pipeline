.PHONY: fetch synthetic render pages load dbt smoke ci-smoke test check-databricks load-databricks dbt-databricks export databricks

# Local, offline: build the data and run the staging models on Spark with Delta tables.
fetch:
	python -m renewal_review.fetch_sources

synthetic:
	python -m renewal_review.synthetic

render:
	python -m renewal_review.render

pages:
	python -m renewal_review.pages

load:
	python -m renewal_review.load_raw --target local

# Extraction needs ai_query, which only exists on Databricks, so locally we stop at staging.
dbt:
	cd dbt && dbt build --select staging --indirect-selection cautious

test:
	pytest -q

smoke: test fetch synthetic render pages load dbt

# Same local steps on a small set of pairs, so a CI run stays quick.
ci-smoke:
	python -m renewal_review.fetch_sources
	python -m renewal_review.synthetic --pairs 12
	python -m renewal_review.render
	python -m renewal_review.pages
	python -m renewal_review.load_raw --target local
	cd dbt && dbt build --select staging --indirect-selection cautious

# Full pipeline on Databricks. Needs DATABRICKS_* in .env.
check-databricks:
	python -m renewal_review.databricks_check

load-databricks:
	python -m renewal_review.load_raw --target databricks

dbt-databricks:
	cd dbt && dbt build --target databricks

export:
	python -m renewal_review.export_results

databricks: fetch synthetic render pages check-databricks load-databricks dbt-databricks export
