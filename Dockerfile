FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless make curl \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 \
    SPARK_CONF_DIR=/app/conf \
    DBT_PROFILES_DIR=/app/dbt \
    PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download the Delta jars once at build time so runs work offline.
COPY conf/ conf/
RUN python -c "from pyspark.sql import SparkSession; SparkSession.builder.getOrCreate().stop()"

COPY . .
