"""Shared Spark session. Settings come from conf/spark-defaults.conf."""
from pyspark.sql import SparkSession


def get_spark(app_name: str = "renewal-review") -> SparkSession:
    return SparkSession.builder.appName(app_name).getOrCreate()
