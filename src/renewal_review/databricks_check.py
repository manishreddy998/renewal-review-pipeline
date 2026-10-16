"""Check the Databricks SQL warehouse connection and list what we can see."""
import os

from databricks import sql


def connect():
    return sql.connect(
        server_hostname=os.environ["DATABRICKS_HOST"],
        http_path=os.environ["DATABRICKS_HTTP_PATH"],
        access_token=os.environ["DATABRICKS_TOKEN"],
    )


def main() -> None:
    with connect() as conn, conn.cursor() as cur:
        cur.execute("select 1, current_catalog(), current_schema(), current_user()")
        print("connected:", cur.fetchone())
        cur.execute("show catalogs")
        print("catalogs:", [r[0] for r in cur.fetchall()])


if __name__ == "__main__":
    main()
