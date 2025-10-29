# 🚀 Data Pipeline with Airflow, dbt, and Cosmos: CSV to BigQuery ETL

This project implements a complete **Extract, Transform, Load (ETL)** data pipeline using **Apache Airflow** for orchestration, **dbt (data build tool)** for data transformation, and **Cosmos** for seamless dbt integration within Airflow.

The pipeline processes a local CSV file, loads it into a **Google BigQuery** raw layer, and then uses dbt to perform transformations, creating a final, clean data mart.

---

## ✨ Key Features

* **Orchestration:** Managed by **Apache Airflow**.
* **Transformation:** Handled by **dbt** with models structured in `staging` and `marts` layers.
* **Integration:** **Cosmos** simplifies dbt execution directly within the Airflow DAG.
* **Data Storage:** **Google BigQuery** is used as the data warehouse.
* **Local Setup:** Dockerized environment for easy and consistent deployment.

---

## 📂 Project Structure

The repository is structured to separate the Airflow and dbt components, following best practices for a data engineering project.

---

## 🛠️ Technology Stack

| Tool | Purpose |
| :--- | :--- |
| **Apache Airflow** | Orchestration of the entire pipeline. |
| **dbt (data build tool)** | SQL-based data transformation (T in ETL). |
| **Astronomer Cosmos** | Airflow extension to seamlessly run dbt projects. |
| **Google BigQuery** | Cloud data warehouse for storage and processing. |
| **Docker** | Containerization for a reproducible local development environment. |

---

## 💡 Pipeline Workflow (`users_bq_dbt_pipeline`)

The main Airflow DAG, `users_bq_dbt_pipeline`, executes the following steps:

1.  **`start`** (`EmptyOperator`): Marks the beginning of the DAG run.
2.  **`create_datasets`** (`PythonOperator`): Ensures the **`raw`** and **`users_dbt`** BigQuery datasets exist.
3.  **`load_csv_to_bq_raw`** (`PythonOperator`): Loads the `data/users.csv` file into the `raw.users` table in BigQuery.
4.  **`dbt_build`** (`DbtTaskGroup` via **Cosmos**):
    * Runs all dbt models (`dbt build`).
    * Models in `staging` are created first.
    * Final mart models (`dim_users`) are created in the `users_dbt` dataset.
5.  **`end`** (`EmptyOperator`): Marks the successful completion of the DAG.

---

## ⚙️ Setup and Installation

### Prerequisites

* Docker and Docker Compose installed.
* A Google Cloud Project configured.
* A Google Service Account Key (`gcp-sa.json`) with **BigQuery Data Editor** and **BigQuery Job User** roles.

### Steps

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/HugoDias05/pipeline-dbt-cosmos-airflow
    cd [YOUR REPO FOLDER]
    ```

2.  **Configure Environment Variables:**
    Create a `.env` file in the root directory and populate it with your environment-specific values:
    ```bash
    # .env file content
    GCP_PROJECT_ID="your-gcp-project-id"
    BIGQUERY_DATASET="users_dbt" # Or your desired dataset name
    BIGQUERY_LOCATION="US"       # Or your desired BigQuery region (e.g., EU)

    # Airflow specific (optional, defaults provided in docker-compose)
    AIRFLOW_UID=50000 
    AIRFLOW_DAGS=./dags
    AIRFLOW_LOGS=./logs
    AIRFLOW_PLUGINS=./plugins
    AIRFLOW_SECRETS=./secrets
    ```

3.  **Place Credentials:**
    * Create a `secrets` directory: `mkdir secrets`.
    * Place your Google Service Account JSON file into the `secrets` folder and rename it to **`gcp-sa.json`**.
    * Place your source data into the `data` folder as **`users.csv`**.

4.  **Build and Run with Docker Compose:**
    The provided `docker-compose.yml` uses a custom `Dockerfile` to build an Airflow image that includes all necessary dependencies (**dbt, Cosmos, BigQuery providers**).

    ```bash
    docker compose up -d --build
    ```

5.  **Access Airflow:**
    The Airflow UI will be available at `http://localhost:8080`.
    * **Username:** `airflow`
    * **Password:** `airflow`

6.  **Run the DAG:**
    * In the Airflow UI, find the **`users_bq_dbt_pipeline`** DAG.
    * Unpause the DAG and trigger a run to start the ETL process!

---

## 👤 Author

* **Name:** Hugo Dias
* **LinkedIn:** https://www.linkedin.com/in/hugoduartedias/
* **GitHub:** https://github.com/HugoDias05
* **Project Date:** October, 2025
