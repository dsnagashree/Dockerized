# stock_pipeline/Dockerfile
FROM apache/airflow:2.8.0

# Install required Airflow provider packages
RUN pip install --no-cache-dir "apache-airflow-providers-postgres"

# Install Python libraries for your data pipeline script
RUN pip install --no-cache-dir "requests" "psycopg2-binary"