FROM apache/airflow:2.7.1
USER root
RUN apt-get update && apt-get install -y --no-install-recommends build-essential git gcc \
 && rm -rf /var/lib/apt/lists/*
USER airflow
RUN pip install --no-cache-dir \
    astronomer-cosmos==1.2.5 \
    dbt-core==1.7.* \
    dbt-bigquery==1.7.* \
    google-cloud-bigquery==3.* \
    pandas-gbq==0.20.* \
    pyarrow>=14.0.0
