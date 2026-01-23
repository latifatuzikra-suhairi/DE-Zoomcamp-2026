#!/usr/bin/env python
# coding: utf-8

# In[4]:


#library
import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# function
def load_env():
    load_dotenv()
    return {
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "host": os.getenv("POSTGRES_HOST"),
        "port": os.getenv("POSTGRES_PORT"),
        "db": os.getenv("POSTGRES_DB"),
    }


def download_data():
    os.makedirs("data", exist_ok=True)

    parquet_url = "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet"
    csv_url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"

    os.system(f"wget -c {parquet_url} -P data")
    os.system(f"wget -c {csv_url} -P data")


def read_data():
    parquet_path = "data/green_tripdata_2025-11.parquet"
    csv_path = "data/taxi_zone_lookup.csv"

    df_parquet = pd.read_parquet(parquet_path)
    df_csv = pd.read_csv(csv_path)

    return df_parquet, df_csv


def create_db_engine(env):
    url = f"postgresql://{env['user']}:{env['password']}@{env['host']}:{env['port']}/{env['db']}"
    return create_engine(url)


def batch_insert(df, engine, table_name, chunk_size=10000):
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=chunk_size
    )

if __name__ == "__main__":
    env = load_env()

    download_data()
    df_trip, df_zone = read_data()

    engine = create_db_engine(env)

    # Insert
    batch_insert(df_trip, engine, table_name="green_tripdata")
    batch_insert(df_zone, engine, table_name="taxi_zone_lookup")

