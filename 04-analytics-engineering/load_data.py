import os
import sys
import urllib.request
from itertools import product
from concurrent.futures import ThreadPoolExecutor
from google.cloud import storage, bigquery
from google.api_core.exceptions import NotFound
import time

# =============================
# CONFIG
# =============================

PROJECT_ID = "zoomcamp-dbt-487603"
BUCKET_NAME = "zoomcamp_dbt_hw4"
DATASET_NAME = "ny_taxi"

YEARS = ["2019", "2020"]
MONTHS = [f"{i:02d}" for i in range(1, 13)]
COLORS = ["yellow", "green"]

DOWNLOAD_DIR = "./data"
MAX_WORKERS = 6

BASE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download"

# =============================
# INIT CLIENTS
# =============================

storage_client = storage.Client(project=PROJECT_ID)
bq_client = bigquery.Client(project=PROJECT_ID)

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# =============================
# DOWNLOAD
# =============================

def download_file(params):
    color, year, month = params
    file_name = f"{color}_tripdata_{year}-{month}.csv.gz"
    url = f"{BASE_URL}/{color}/{file_name}"
    file_path = os.path.join(DOWNLOAD_DIR, file_name)

    if os.path.exists(file_path):
        return file_path

    try:
        print(f"Downloading {file_name}")
        urllib.request.urlretrieve(url, file_path)
        return file_path
    except Exception as e:
        print(f"Failed {file_name}: {e}")
        return None


# =============================
# GCS
# =============================

def create_bucket():
    try:
        storage_client.get_bucket(BUCKET_NAME)
        print("Bucket exists")
    except NotFound:
        storage_client.create_bucket(BUCKET_NAME)
        print("Bucket created")


def upload_to_gcs(file_path):
    bucket = storage_client.bucket(BUCKET_NAME)
    blob_name = os.path.basename(file_path)
    blob = bucket.blob(blob_name)

    print(f"Uploading {blob_name}")
    blob.upload_from_filename(file_path)


# =============================
# BIGQUERY
# =============================

def create_dataset():
    dataset_id = f"{PROJECT_ID}.{DATASET_NAME}"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "US"

    try:
        bq_client.get_dataset(dataset_id)
        print("Dataset exists")
    except Exception:
        bq_client.create_dataset(dataset)
        print("Dataset created")


def load_to_bigquery(color):
    table_id = f"{PROJECT_ID}.{DATASET_NAME}.{color}_nytaxi"

    uri = f"gs://{BUCKET_NAME}/{color}_tripdata_*.csv.gz"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition="WRITE_APPEND",
    )

    print(f"Loading {color} data to BigQuery...")

    load_job = bq_client.load_table_from_uri(
        uri,
        table_id,
        job_config=job_config,
    )

    load_job.result()
    print(f"Loaded into {table_id}")


# =============================
# MAIN
# =============================

if __name__ == "__main__":

    create_bucket()
    create_dataset()

    tasks = list(product(COLORS, YEARS, MONTHS))

    print("Downloading files...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        files = list(executor.map(download_file, tasks))

    files = list(filter(None, files))

    print("Uploading files to GCS...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(upload_to_gcs, files)

    print("Loading to BigQuery...")
    for color in COLORS:
        load_to_bigquery(color)

    print("Pipeline completed successfully 🚀")