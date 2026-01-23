# Module 1: Docker & Data Ingestion Using Postgres

### Question 1. Understanding Docker Images 
1. Creating a Docker image Python 3.13
```bash
docker run -it --rm \
  -v $(pwd):/app \
  --entrypoint=bash \
  python:3.13

```
2. Check the pip version
```bash
pip --version
```

**Answer**
The pip version of the Python 3.13 Docker image is **25.3**
![Question 1 - PIP Version](../images/01_Q1_pip-version.png)

---
### Question 2. Understanding Docker Networking and Docker-Compose
1. Create ``docker-compose.yaml``
fill the file with the existing script from the question
```bash
services:
  # this is container for postgres (the database)
  db: #hostname
    container_name: postgres #container name in docker
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'  #postgres username
      POSTGRES_PASSWORD: 'postgres'  #postgres password
      POSTGRES_DB: 'ny_taxi'  #postgres db name
    ports:
      - '5433:5432'   #port on host machine : port inside the container
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  # this is container for pgadmin (GUI database)
  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: "pgadmin@pgadmin.com"   # use this to login into pgadmin4
      PGADMIN_DEFAULT_PASSWORD: "pgadmin"  # use this to login into pgadmin4
    ports:
      - "8080:80"   # this is port to access to our pgadmin, http://localhost:8080
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin

volumes:
  vol-pgdata:
    name: vol-pgdata
  vol-pgadmin_data:
    name: vol-pgadmin_data
```
2. Run the docker-compose.yaml
```bash
pip --version
```bash
docker compose up -d
```
3. Run pgadmin4 
Access pgAdmin in browser by browsing to `http://localhost:8080`, and login into pgadmin using `PGADMIN_DEFAULT_EMAIL` and `PGADMIN_DEFAULT_PASSWORD` state in the `docker-compose.yaml` file.

4. Create new server
Register the server connection refers to our configuration on the `docker-compose.yaml`:
- hostname : `db`
- port : `5432`
- username : `postgres`
- password : `postgres`

![Question 2 - pgAdmin Server](../images/01_Q2_setup-pgadmin.png)

**Answer**
Based on the docker-compose.yaml, the right choice is `db:5432`

Notes: [Docker Compose — Ports documentation](https://docs.docker.com/reference/compose-file/services/#ports)

---
### Data Preparation to Answer Q3-Q6
To prepare the data needed for answering Question 3 to Question 6, I implemented a containerized data pipeline using Docker. The goal of this preparation is to reliably download CSV data, process it in batches using Python, and load it into a PostgreSQL database for further analysis. 

**Workflow**
![Question 3 - Data Preparation](../images/01_Q3_data-preparation.png)
This workflow follows a two-phase approach:
1. Development Phase 
   Purpose: Explore and validate ingestion logic safely
   What happened here:
   - Inspect CSV data
   - Testing database connection
   - Experiment with batch size logic
   - Prototype insert logic data
   Output: converted notebook script (.ipynb) into python script (.py) → `pipeline.py`

2. Production Phase 
   Purpose: Load data in a repeatable, deterministic, and scalable way
   What happened here:
   - pipeline.py reads raw CSV files
   - Data is inserted into PostgreSQL in batches
   - Script runs via Docker container
   - Can be scheduled or orchestrated later

---
### Question 3. Counting short trips
`Q3 : For the trips in November 2025 (lpep_pickup_datetime between '2025-11-01' and '2025-12-01', exclusive of the upper bound), how many trips had a trip_distance of less than or equal to 1 mile?`




