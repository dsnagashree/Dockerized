
# Dockerized Stock Market Data Pipeline with Airflow

This project demonstrates a fully containerized data pipeline that automatically fetches stock market data from a public API, processes it, and stores it in a PostgreSQL database. The entire workflow is orchestrated using Apache Airflow.

## Project Objective

The pipeline performs the following actions:
- **Fetches Data**: Retrieves stock market data from a free API on a scheduled basis.
- **Processes & Stores**: Parses the JSON response and updates a PostgreSQL table with the extracted information.
- **Ensures Robustness**: Includes comprehensive error handling to manage missing data and connection failures gracefully.

The entire setup is designed to be easily deployed and managed using Docker Compose.

## Requirements

To run this pipeline, you must have the following software installed on your machine:

- **Docker**: The containerization platform.
- **Docker Compose**: The tool for defining and running multi-container Docker applications.

## Project Structure

The project is organized into the following key directories and files:

```

stock_pipeline/
├── dags/
│   └── stock_dag.py             # Airflow DAG file with pipeline logic
├── data_pipeline/
│   ├── __init__.py              # Marks the directory as a Python package
│   ├── fetch_data.py            # The core Python script for data fetching and storage
│   └── requirements.txt         # Python libraries for the data script
├── .env                         # Secure file for storing environment variables (sensitive info)
├── docker-compose.yml           # Defines and orchestrates all Docker services
├── Dockerfile                   # Builds a custom Airflow image with required dependencies
└── README.md                    # This file

```

## Setup and Running the Pipeline

Follow these steps to get the data pipeline up and running.

### 1. Configure Environment Variables

Create a `.env` file in the root directory of the project and fill it with your API key and database credentials. This file is ignored by Git to prevent sensitive information from being pushed to your repository.

`.env`  
Replace the values with your actual API key and credentials:

```

STOCK\_API\_KEY=YOUR\_API\_KEY\_HERE
STOCK\_API\_NAME=YOUR\_API\_NAME\_HERE
STOCK\_SYMBOL=YOUR\_STOCK\_SYMBOL

DB\_USER=airflow
DB\_PASSWORD=airflow
DB\_NAME=stocks

````

### 2. Build and Run the Docker Containers

Run these commands from your project's root directory in the terminal.

- Build the Images and Initialize Airflow's Database:  
  This command builds the custom Docker image and runs the `airflow-init` service to set up Airflow's metadata database in PostgreSQL. This is a one-time setup step.
  ```sh
  docker compose up --build airflow-init
  ```
- Start the Airflow Services:
  This command starts the Airflow webserver and scheduler in the background.
  ```sh
  docker compose up -d
  ```
## Using the Airflow UI to Run the Pipeline

Once the services are running, you can use the Airflow web UI to monitor and trigger your pipeline.

1. **Access the UI**: Open your web browser and go to `http://localhost:8080`.
2. **Log in**: Use the default credentials:

   * **Username**: `airflow`
   * **Password**: `airflow`
3. **Unpause and Trigger**: On the main dashboard, find the `stock_data_pipeline` DAG. Unpause it by toggling the button. You can then manually trigger a run by clicking the play button.

## Final Data Verification

After a successful DAG run, you can verify that the data was written to the database.

1. **Open a terminal for the database container**: In Docker Desktop, go to the `postgres_db` container and click the **CLI** button.
2. **Connect to the database**: Run the `psql` command with your credentials:

   ```sh
   psql -U airflow -d stocks
   ```
3. **Query the data**: Run a `SELECT` statement to view the contents of the `stock_data` table.

   ```sql
   SELECT * FROM stock_data;
   ```








