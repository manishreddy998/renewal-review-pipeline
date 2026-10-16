# Renewal Review Pipeline

A small data pipeline that reads last year's policy and the renewal offer for the same client,
pulls out the key fields, compares them, and ranks the accounts a broker should look at first.

Every value keeps a pointer back to the document and page it came from, and each agency only
sees its own data.

Status: early setup. More sections will be added as each part is built.

## Run it

Everything runs in Docker.

```
docker compose build
docker compose run --rm app make smoke
```

`make smoke` runs the tests, downloads the FSRA OAP 1 policy wording, builds the synthetic
answer key, and runs dbt against local Delta tables.

To run on Databricks later, copy `.env.example` to `.env`, fill in the workspace values, and run
`dbt build --target databricks` from the `dbt` folder.

## Docs

- `docs/sources.md`: where the public data comes from and license notes
- `docs/synthetic-data-plan.md`: how the test policies are made
