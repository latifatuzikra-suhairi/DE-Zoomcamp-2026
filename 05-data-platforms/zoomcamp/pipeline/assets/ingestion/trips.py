"""@bruin
name: ingestion.trips
type: python
image: python:3.11
connection: duckdb-default   

materialization:
  type: table
  strategy: append

columns:
  - name: pickup_datetime
    type: timestamp
    description: "When the meter was engaged"
    checks:
      - name: not_null

  - name: dropoff_datetime
    type: timestamp
    description: "When the meter was disengaged"
@bruin"""

import os
import json
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
import requests
import tempfile


BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"


def strip_tz_from_table(table: pa.Table) -> pa.Table:
    new_columns = []
    new_fields = []
    for i, field in enumerate(table.schema):
        col = table.column(i)
        if pa.types.is_timestamp(field.type) and field.type.tz is not None:
            new_type = pa.timestamp(field.type.unit)
            col = col.cast(new_type)
            field = field.with_type(new_type)
        new_columns.append(col)
        new_fields.append(field)
    return pa.table(
        dict(zip([f.name for f in new_fields], new_columns)),
        schema=pa.schema(new_fields)
    )


def download_parquet(url: str) -> pa.Table:
    """Download parquet from URL into a temp file, then read it."""
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
        for chunk in response.iter_content(chunk_size=8192):
            tmp.write(chunk)
        tmp_path = tmp.name

    try:
        table = pq.read_table(tmp_path)
    finally:
        os.remove(tmp_path)  # clean up temp file

    return table


def materialize():
    start_date = os.environ["BRUIN_START_DATE"]
    end_date = os.environ["BRUIN_END_DATE"]

    vars_json = json.loads(os.environ.get("BRUIN_VARS", "{}"))
    taxi_types = vars_json.get("taxi_types", ["yellow"])

    months = pd.date_range(start=start_date, end=end_date, freq="MS")

    dfs = []

    for taxi_type in taxi_types:
        for dt in months:
            year = dt.year
            month = f"{dt.month:02d}"
            url = f"{BASE_URL}/{taxi_type}_tripdata_{year}-{month}.parquet"
            print(f"Downloading: {url}")

            try:
                arrow_table = download_parquet(url)
                arrow_table = strip_tz_from_table(arrow_table)
                df = arrow_table.to_pandas()

                df = df.rename(columns={
                    "tpep_pickup_datetime": "pickup_datetime",
                    "tpep_dropoff_datetime": "dropoff_datetime"
                })

                df["taxi_type"] = taxi_type
                dfs.append(df)
                print(f"  -> Loaded {len(df)} rows")

            except Exception as e:
                print(f"Skipping {url} -> {e}")

    if len(dfs) == 0:
        raise ValueError("No parquet files were loaded.")

    final_dataframe = pd.concat(dfs, ignore_index=True)
    print("Total rows loaded:", len(final_dataframe))
    return final_dataframe

