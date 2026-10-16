"""Load the raw tables into local Delta (Spark) or Databricks.

    python -m renewal_review.load_raw --target local
    python -m renewal_review.load_raw --target databricks
"""
import argparse
import os

from renewal_review.raw_tables import TABLES

BATCH = 50


def load_local() -> None:
    from renewal_review.spark import get_spark

    spark = get_spark()
    spark.sql("create schema if not exists raw")
    for name, (build, schema) in TABLES.items():
        # Dates arrive as text, so load them as strings and cast in Spark.
        ddl = ", ".join(f"{c} {'string' if t == 'date' else t}" for c, t in schema.items())
        df = spark.createDataFrame(build(), schema=ddl)
        df = df.selectExpr(*[f"cast({c} as {t}) as {c}" for c, t in schema.items()])
        df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"raw.{name}")
        print(f"raw.{name}: {df.count()} rows")


def load_databricks() -> None:
    from renewal_review.databricks_check import connect

    catalog = os.environ.get("DATABRICKS_CATALOG", "workspace")
    with connect() as conn, conn.cursor() as cur:
        cur.execute(f"create schema if not exists {catalog}.raw")
        for name, (build, schema) in TABLES.items():
            table = f"{catalog}.raw.{name}"
            cols = list(schema)
            ddl = ", ".join(f"{c} {t}" for c, t in schema.items())
            cur.execute(f"create or replace table {table} ({ddl}) using delta")
            rows = build()
            for start in range(0, len(rows), BATCH):
                chunk = rows[start:start + BATCH]
                params, values = {}, []
                for i, row in enumerate(chunk):
                    names = []
                    for c in cols:
                        key = f"{c}_{i}"
                        params[key] = row[c]
                        names.append(f"cast(:{key} as {schema[c]})")
                    values.append("(" + ", ".join(names) + ")")
                cur.execute(f"insert into {table} ({', '.join(cols)}) values {', '.join(values)}", params)
            cur.execute(f"select count(*) from {table}")
            print(f"{table}: {cur.fetchone()[0]} rows")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=["local", "databricks"], default="local")
    args = parser.parse_args()
    load_local() if args.target == "local" else load_databricks()


if __name__ == "__main__":
    main()
