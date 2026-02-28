"""@bruin
name: ingestion.trips
type: python
image: python:3.11

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


BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"


def materialize():
    start_date = os.environ["BRUIN_START_DATE"]
    end_date = os.environ["BRUIN_END_DATE"]

    vars_json = json.loads(os.environ.get("BRUIN_VARS", "{}"))
    taxi_types = vars_json.get("taxi_types", ["yellow"])

    # Generate monthly intervals
    months = pd.date_range(
        start=start_date,
        end=end_date,
        freq="MS"   # Month Start
    )

    dfs = []

    for taxi_type in taxi_types:
        for dt in months:
            year = dt.year
            month = f"{dt.month:02d}"

            url = f"{BASE_URL}/{taxi_type}_tripdata_{year}-{month}.parquet"

            print(f"Downloading: {url}")

            try:
                df = pd.read_parquet(url)
                df["taxi_type"] = taxi_type  # useful downstream
                dfs.append(df)

            except Exception as e:
                print(f"Skipping {url} -> {e}")

    if len(dfs) == 0:
        raise ValueError("No parquet files were loaded.")

    final_dataframe = pd.concat(dfs, ignore_index=True)

    print("Total rows loaded:", len(final_dataframe))

    return final_dataframe