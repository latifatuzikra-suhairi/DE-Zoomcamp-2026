# Module 3: Data Warehouse
## Overview
This repository contains my solutions for Module 3 of the Data Engineering Zoomcamp. In this module, I explored data warehousing and analytics using Google BigQuery, covering data ingestion, external vs materialized tables, and dataset/schema management. I analyzed query performance using bytes processed and applied partitioning and clustering strategies to optimize query efficiency and reduce storage and compute costs.

### Tech Stack
- Google Cloud Storage (GCS) — Cloud object storage for raw data
- Google BigQuery — Serverless data warehouse for analytics, partitioning, and clustering

## 📝 Homework
### GCP Setup
For this homework we will be using the Yellow Taxi Trip Records for January 2024 - June 2024 that can be found here: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

Steps:
To do the homework, we need to setup GCP and load the data into Google Cloud Storage. 
1. Load data into Google Cloud Storage
- Create new project in the Google Cloud Platform. In this case, i used `zoomcamp-dw` as my project name
- Create a GCS bucket in the project, mine is `zoomcamp_hw3`
- Authenticate using Google Cloud SDK (ADC). I used ADC instead using credentials file.
```bash
gcloud auth login
gcloud config set project (PROJECT_ID)
gcloud auth application-default login
```
- Using [load_yellow_taxi_data.py](load_yellow_taxi_data.py), update the `project_id` and `bucket_name` based on the GCP configuration.
- Run the python script using:
```bash
python load_yellow_taxi_data.py
```
The script will upload the data to the GCS bucket. A successful run will produce output similar to the following:
![Homework 3 - Load Data Into GCS](../images/03_load-data-to-GCS.png)

2. BigQuery Setup
- Create schema
```sql
CREATE SCHEMA IF NOT EXISTS 
  `zoomcamp-dw-486814.nyc_taxi`
OPTIONS (location = 'US');
```

- Create external table
```sql
CREATE OR REPLACE EXTERNAL TABLE
  `zoomcamp-dw-486814.nyc_taxi.external_yellow_tripdata_2024`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://zoomcamp_hw3/yellow_tripdata_2024-*.parquet']
);
```

- Create materialized table
```sql
CREATE OR REPLACE TABLE
`zoomcamp-dw-486814.nyc_taxi.yellow_tripdata_2024`
AS
SELECT *
FROM `zoomcamp-dw-486814.nyc_taxi.external_yellow_tripdata_2024`;
```
After completing these steps, the dataset contains both the external table (backed by data in GCS) and the native BigQuery table, as shown below:
![Homework 3 - BigQuery Setup](../images/03_bigquery-setup.png)

<hr>

### Question 1. Counting records
> What is count of records for the 2024 Yellow Taxi Data?
```sql
    SELECT COUNT(*) AS total_records
    FROM `zoomcamp-dw-486814.nyc_taxi.yellow_tripdata_2024`;
```
**✅ Answer**: <br>
count of records for the 2024 Yellow Taxi Data **20,332,093**

<hr>

### Question 2. Data read estimation
> Write a query to count the distinct number of PULocationIDs for the entire dataset on both the tables.
> What is the estimated amount of data that will be read when this query is executed on the External Table and the Table?
>
> - 18.82 MB for the External Table and 47.60 MB for the Materialized Table
> - 0 MB for the External Table and 155.12 MB for the Materialized Table
> - 2.14 GB for the External Table and 0MB for the Materialized Table
> - 0 MB for the External Table and 0MB for the Materialized Table

```sql
# Q2: a. Write a query to count the distinct number of PULocationIDs for external table.
SELECT COUNT(DISTINCT PULocationID) AS num_PULocationID
FROM `zoomcamp-dw-486814.nyc_taxi.external_yellow_tripdata_2024`;

# Q2: b. Write a query to count the distinct number of PULocationIDs for materialized table.
SELECT COUNT(DISTINCT PULocationID) AS num_PULocationID
FROM `zoomcamp-dw-486814.nyc_taxi.yellow_tripdata_2024`;
```
**✅ Answer**: <br>
To check the estimated amount of data processed by a query, select the query in the BigQuery editor. BigQuery will automatically display the estimated bytes to be read before execution.

<p float="left">
  <img src="../images/03_Q2_external-table.png" width="48%" />
  <img src="../images/03_Q2_materialized-table.png" width="48%" />
</p>

So, the right answer is  **0 MB for the External Table and 155.12 MB for the Materialized Table**

<hr>

### Question 3. Understanding columnar storage
> Write a query to retrieve the PULocationID from the table (not the external table) in BigQuery. Now write a query to retrieve the PULocationID and DOLocationID on the same table.
>
> Why are the estimated number of Bytes different?
> - BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed.
> - BigQuery duplicates data across multiple storage partitions, so selecting two columns instead of one requires scanning the table twice, doubling the estimated bytes processed.
> - BigQuery automatically caches the first queried column, so adding a second column increases processing time but does not affect the estimated bytes scanned.
> - When selecting multiple columns, BigQuery performs an implicit join operation between them, increasing the estimated bytes processed

**✅ Answer**: <br>
The estimated number of bytes is different because BigQuery is a columnar database and only scans the columns referenced in the query. The right choice is **BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed.**

<hr>

### Question 4. Counting zero fare trips
> How many records have a fare_amount of 0?

```sql
SELECT COUNT(vendorID) AS zero_fare_trips
FROM `zoomcamp-dw-486814.nyc_taxi.yellow_tripdata_2024`
WHERE fare_amount = 0;
```
**✅ Answer**: <br>
There are **8333** records having 0 fare_amount.



