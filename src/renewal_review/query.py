"""Run a SQL statement on Databricks and print the result as a table.

    python -m renewal_review.query "select count(*) from workspace.renewal_review.mart_renewal_queue"
"""
import sys

from renewal_review.databricks_check import connect


def run(sql: str) -> tuple[list[str], list[tuple]]:
    with connect() as conn, conn.cursor() as cur:
        cur.execute(sql)
        cols = [d[0] for d in cur.description]
        return cols, [tuple(r) for r in cur.fetchall()]


def main() -> None:
    cols, rows = run(sys.argv[1])
    widths = [max(len(str(c)), *(len(str(r[i])) for r in rows)) if rows else len(c) for i, c in enumerate(cols)]
    print("  ".join(str(c).ljust(w) for c, w in zip(cols, widths)))
    for r in rows:
        print("  ".join(str(v).ljust(w) for v, w in zip(r, widths)))


if __name__ == "__main__":
    main()
