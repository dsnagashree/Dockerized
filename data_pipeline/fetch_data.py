# data_pipeline/fetch_data.py

import os
import requests
import psycopg2
import json

def get_api_endpoint(api_name, api_key, symbol):
    """
    Returns the API URL for a given stock API and symbol.
    """
    api_endpoints = {
        "alpha_vantage": f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={api_key}",
        "finnhub": f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}"
    }
    return api_endpoints.get(api_name)

def fetch_and_store_data():
    """
    Fetches stock data from an API and stores it in a PostgreSQL database.
    """
    # 1. Configuration from Environment Variables
    API_KEY = os.environ.get("STOCK_API_KEY")
    API_NAME = os.environ.get("STOCK_API_NAME", "alpha_vantage")
    STOCK_SYMBOL = os.environ.get("STOCK_SYMBOL", "IBM")
    DB_HOST = os.environ.get("DB_HOST")
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_NAME = os.environ.get("DB_NAME")

    if not all([API_KEY, DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
        print("Missing one or more required environment variables.")
        return

    api_url = get_api_endpoint(API_NAME, API_KEY, STOCK_SYMBOL)
    if not api_url:
        print(f"Invalid API name: {API_NAME}")
        return

    # 2. Fetch Data from the API
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        print("Successfully fetched data from API.")

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return
    except json.JSONDecodeError:
        print("Failed to decode JSON from API response. Response may not be JSON.")
        return

    # 3. Process and Extract Data
    try:
        extracted_data = []
        if API_NAME == "finnhub":
            # Finnhub "quote" endpoint returns a single set of values, not a time series.
            # You would need to use a different endpoint for a time series (e.g., /stock/candle)
            # This example handles the /quote endpoint, which is simpler for demonstration.
            if data.get("t"): # Check if a timestamp exists
                extracted_data.append({
                    "timestamp": data["t"],
                    "open": data.get("o"),
                    "high": data.get("h"),
                    "low": data.get("l"),
                    "close": data.get("c"),
                    "volume": data.get("v")
                })
        
        elif API_NAME == "alpha_vantage":
            # Existing Alpha Vantage parsing logic
            time_series = data.get("Time Series (5min)", {})
            if not time_series:
                print("No time series data found. Handling gracefully.")
                return

            for timestamp, values in time_series.items():
                extracted_data.append({
                    "timestamp": timestamp,
                    "open": values.get("1. open"),
                    "high": values.get("2. high"),
                    "low": values.get("3. low"),
                    "close": values.get("4. close"),
                    "volume": values.get("5. volume")
                })

        if not extracted_data:
            print("No data extracted. Please check API response format or symbol.")
            return

        print(f"Extracted {len(extracted_data)} data points.")

    except (KeyError, IndexError) as e:
        print(f"Error parsing JSON data: missing key or index {e}. Data may be malformed.")
        return

    # 4. Connect to and Update the PostgreSQL Database
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS stock_data (
            timestamp TIMESTAMP PRIMARY KEY,
            open NUMERIC,
            high NUMERIC,
            low NUMERIC,
            close NUMERIC,
            volume INTEGER
        );
        """
        cursor.execute(create_table_sql)
        conn.commit()

        insert_sql = """
        INSERT INTO stock_data (timestamp, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (timestamp) DO UPDATE
        SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            volume = EXCLUDED.volume;
        """

        for row in extracted_data:
            cursor.execute(insert_sql, (
                row["timestamp"],
                row["open"],
                row["high"],
                row["low"],
                row["close"],
                row["volume"]
            ))

        conn.commit()
        print("Successfully updated the PostgreSQL table.")

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    fetch_and_store_data()
    