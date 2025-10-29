from datetime import datetime, timedelta
import os
import pandas as pd

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator

# Cosmos (dbt orchestration)
from cosmos import DbtTaskGroup
from cosmos.config import ProjectConfig, ProfileConfig


# -----------------------------
# VARIÁVEIS GLOBAIS
# -----------------------------
DAG_ID = "users_bq_dbt_pipeline"

# CSV agora está na pasta "data/" (montada como /opt/airflow/data)
DATA_CSV_PATH = "/opt/airflow/data/users.csv"

# Variáveis de ambiente (vindas do docker-compose)
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", "users_dbt")
BIGQUERY_LOCATION = os.environ.get("BIGQUERY_LOCATION", "US")
RAW_DATASET = "raw"  # dataset da camada bruta


# -----------------------------
# FUNÇÕES PYTHON
# -----------------------------
def create_datasets_if_not_exists():
    """
    Cria os datasets 'raw' e 'users_dbt' no BigQuery, caso ainda não existam.
    """
    from google.cloud import bigquery
    client = bigquery.Client()

    for dataset_name in [RAW_DATASET, BIGQUERY_DATASET]:
        dataset_id = f"{client.project}.{dataset_name}"
        try:
            client.get_dataset(dataset_id)
            print(f"Dataset já existe: {dataset_id}")
        except Exception:
            dataset = bigquery.Dataset(dataset_id)
            dataset.location = BIGQUERY_LOCATION
            client.create_dataset(dataset)
            print(f"Dataset criado: {dataset_id}")


def load_csv_to_bigquery_raw():
    """
    Carrega o arquivo CSV local para a tabela raw.users no BigQuery.
    """
    import pandas_gbq

    if not os.path.exists(DATA_CSV_PATH):
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {DATA_CSV_PATH}")

    df = pd.read_csv(DATA_CSV_PATH)
    table_id = f"{GCP_PROJECT_ID}.{RAW_DATASET}.users"

    # Carrega substituindo a tabela existente
    pandas_gbq.to_gbq(
        dataframe=df,
        destination_table=table_id,
        project_id=GCP_PROJECT_ID,
        if_exists="replace",
    )

    print(f"✅ {len(df)} registros carregados em {table_id}")


# -----------------------------
# CONFIG PADRÃO DO DAG
# -----------------------------
default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    description="Pipeline ETL: CSV → BigQuery → Transformação dbt via Cosmos",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2025, 4, 22),
    catchup=False,
    max_active_runs=1,
) as dag:

    # -------------------------
    # TASKS DO PIPELINE
    # -------------------------

    start = EmptyOperator(task_id="start")

    make_datasets = PythonOperator(
        task_id="create_datasets",
        python_callable=create_datasets_if_not_exists,
    )

    load_raw = PythonOperator(
        task_id="load_csv_to_bq_raw",
        python_callable=load_csv_to_bigquery_raw,
    )

    
    project_config = ProjectConfig(
    dbt_project_path="/opt/airflow/dags/dbt"   # diretório que contém dbt_project.yml
    )

    profile_config = ProfileConfig(
        profile_name="users_dbt_profile",          # deve bater com o nome do profile no profiles.yml
        target_name="dev",                         # deve bater com o target do profiles.yml
        profiles_yml_filepath="/opt/airflow/dags/dbt/profiles.yml"  # caminho completo do profiles.yml
    )

    # IMPORT DO DbtTaskGroup (algumas versões usam este caminho alternativo)
    try:
        from cosmos import DbtTaskGroup
    except ImportError:
        from cosmos.airflow.task_group import DbtTaskGroup  # fallback para versões antigas

    dbt_transform = DbtTaskGroup(
    group_id="dbt_build",
    project_config=project_config,
    profile_config=profile_config,
    operator_args={
        "install_deps": True,
        "full_refresh": True,
        "append_env": True,  # 👈 repassa variáveis do Airflow pro subprocesso
        "env": {             # 👇 garante as envs explícitas
            "GCP_PROJECT_ID": os.environ.get("GCP_PROJECT_ID"),
            "BIGQUERY_DATASET": os.environ.get("BIGQUERY_DATASET"),
            "BIGQUERY_LOCATION": os.environ.get("BIGQUERY_LOCATION"),
            "GOOGLE_APPLICATION_CREDENTIALS": os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
        }
    }
)

    end = EmptyOperator(task_id="end")

    # -------------------------
    # ORDEM DE EXECUÇÃO
    # -------------------------
    start >> make_datasets >> load_raw >> dbt_transform >> end
