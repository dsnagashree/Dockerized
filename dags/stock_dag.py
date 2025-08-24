# stock_pipeline/dags/stock_dag.py
from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

from data_pipeline.fetch_data import fetch_and_store_data

# These are the default arguments that will be applied to all tasks in the DAG
with DAG(
    dag_id="stock_data_pipeline",
    start_date=pendulum.datetime(2025, 8, 24, tz="UTC"),
    schedule="0 * * * *",  # Run the DAG every hour
    catchup=False,
    tags=["stock_data", "etl"],
) as dag:
    
    # Task 1: Create the PostgreSQL table if it doesn't exist
    create_table = PostgresOperator(
        task_id="create_table",
        postgres_conn_id="postgres_default",  # This must match your Airflow connection ID
        sql="""
            CREATE TABLE IF NOT EXISTS stock_data (
                timestamp TIMESTAMP PRIMARY KEY,
                open NUMERIC,
                high NUMERIC,
                low NUMERIC,
                close NUMERIC,
                volume INTEGER
            );
        """
    )
    
    # Task 2: Fetch data from the API and store it in the database
    # This task calls the function from your fetch_data.py script
    fetch_and_store = PythonOperator(
        task_id="fetch_and_store_data",
        python_callable=fetch_and_store_data,
        dag=dag,
    )

    # Set the task dependencies
    # The 'fetch_and_store' task will only run after 'create_table' has completed successfully.
    create_table >> fetch_and_store
    