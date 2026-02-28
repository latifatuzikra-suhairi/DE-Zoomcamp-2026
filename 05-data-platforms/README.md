# Module 5: Data Platforms with Bruin
### Tech Stack
**Bruin** : a data pipeline orchestration tool that helps manage, schedule, and run data workflows (such as SQL or Python transformations) in a structured and reproducible way.

### Setup 
1. Install Bruin CLI: curl -LsSf https://getbruin.com/install/cli | sh
2. Initialize the zoomcamp template: bruin init zoomcamp my-pipeline
3. Configure your .bruin.yml with a DuckDB connection
4. Follow the tutorial in the main module README

After completing the setup, you should have a working NYC taxi data pipeline.

<hr>

## 📝 Homework
### Question 1. Bruin Pipeline Structure
> In a Bruin project, what are the required files/directories?
> - `bruin.yml` and `assets/`
> - `.bruin.yml` and `pipeline.yml` (assets can be anywhere)
> - `.bruin.yml` and `pipeline/` with `pipeline.yml` and `assets/`
> - `pipeline.yml` and `assets/` only

**✅ Answer**: <br>
**The answer is `.bruin.yml` and `pipeline/` with `pipeline.yml` and `assets/`**

**Explanation**: <br>
A Bruin project follows a strict hierarchical structure to ensure the CLI can correctly parse environments and dependencies:
1. **Project Root**: Contains the `.bruin.yml file`. This is the "brain" of the project where you define global settings, environment connections (e.g., BigQuery, Snowflake), and secrets.
2. **Pipeline Level**: Each pipeline must reside in its own dedicated folder containing a `pipeline.yml` file. This file specifies the pipeline's name, execution schedule, and specific variables.
3. **Asset Level**: Every pipeline folder must include an `assets/` directory. This is where your functional code lives—SQL transformations, Python scripts, or R files—along with their corresponding YAML metadata.

### Question 2. Materialization Strategies
> You're building a pipeline that processes NYC taxi data organized by month based on pickup_datetime. Which incremental strategy is best for processing a specific interval period by deleting and inserting data for that time period?
> `append` - always add new rows
> `replace` - truncate and rebuild entirely
> `time_interval` - incremental based on a time column
> `view` - create a virtual table only

**✅ Answer**: <br>
**The answer is `time_interval` - incremental based on a time column**

**Explanation**: <br>
Using `time_interval` is best choice because the data is partitioned by a time column (e.g., `pickup_datetime`). This strategy deletes and reloads only the data within the specified time range (such as a specific month), making it efficient for incremental updates without rebuilding the entire table.

Comparison on each strategy:
<table>
  <thead>
    <tr>
      <th>Strategy</th>
      <th>Action</th>
      <th>Best Use Case</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>append</code></td>
      <td>Adds new rows to the end of the table.</td>
      <td>High-volume logging where duplicates aren't a concern.</td>
    </tr>
    <tr>
      <td><code>replace</code></td>
      <td>Drops the table and recreates it.</td>
      <td>Small lookup tables or dimensions that change entirely.</td>
    </tr>
    <tr>
      <td><code>time_interval</code></td>
      <td><b>Deletes specific time-window, then inserts.</b></td>
      <td>Time-series data (Taxi trips, IoT, Financials).</td>
    </tr>
    <tr>
      <td><code>view</code></td>
      <td>Logic stored as a query, no physical data.</td>
      <td>Real-time needs where storage cost is a secondary concern.</td>
    </tr>
  </tbody>
</table>

### Question 3. Pipeline Variables
> You have the following variable defined in pipeline.yml:
> ```
> variables:
>  taxi_types:
>    type: array
>    items:
>      type: string
>    default: ["yellow", "green"]
> ```
>
> How do you override this when running the pipeline to only process yellow taxis?
> - `bruin run --taxi-types yellow`
> - `bruin run --var taxi_types=yellow`
> - `bruin run --var 'taxi_types=["yellow"]'`
> - `bruin run --set taxi_types=["yellow"]`

**✅ Answer**: <br>
**The answer is `bruin run --var 'taxi_types=["yellow"]'`**

**Explanation** : <br>
The concept follows the format `--var KEY=VALUE`
- The `--var` flag: Bruin uses the `--var` option in the CLI to override custom variables defined in `pipeline.yml` at runtime
- Handling arrays: Because the `taxi_types` variable is defined as an `array`, the override value must be written in a list format that Bruin can parse. Wrapping the array in single quotes (for example, 'taxi_types=["yellow"]') ensures the shell passes the entire bracketed value correctly to the Bruin CLI

### Question 4. Running with Dependencies
> You've modified the `ingestion/trips.py` asset and want to run it plus all downstream assets. Which command should you use?
> - `bruin run ingestion.trips --all`
> - `bruin run ingestion/trips.py --downstream`
> - `bruin run pipeline/trips.py --recursive`
> - `bruin run --select ingestion.trips+`

**✅ Answer**: <br>
**The answer is `bruin run ingestion/trips.py --downstream`**

**Explanation**: <br>
Based on the `run` documentation, [run flag docs](https://getbruin.com/docs/bruin/commands/run.html), the `--downstream` flag used to run alldown asset.

### Question 5. Quality Checks
> You want to ensure the `pickup_datetime column` in your trips table never has `NULL` values. Which quality check should you add to your asset definition?
> - `name: unique`
> - `name: not_null`
> - `name: positive`
> - `name: accepted_values, value: [not_null]`

**✅ Answer**: <br>
**The answer is `name: not_null`**

**Explanation**: <br>
Common data quality checks in Bruin include:
1. `not_null` – Ensures a column does not contain NULL values.
2. `unique` – Ensures all values in a column are unique (no duplicates).
3. `accepted_values` – Ensures column values belong to a predefined list (e.g., ["yes", "no"]).
4. `min` – Ensures the column value is greater than or equal to a specified minimum.
5. `max` – Ensures the column value is less than or equal to a specified maximum.
6. `non-negative` – Ensures verify that the values of the column are all non negative (positive or zero)
7. `positive` – Ensures numeric values are greater than zero.
8. `pattern` – Ensures that the values of the column match a specified regular expression.

### Question 6. Lineage and Dependencies
> After building your pipeline, you want to visualize the dependency graph between assets. Which Bruin command should you use?
> - `bruin graph`
> - `bruin dependencies`
> - `bruin lineage`
> - `bruin show`

**✅ Answer**: <br>
**The answer is `bruin lineage`** 

**Explanation**: <br>
See the [Bruin Lineage Docs](https://getbruin.com/docs/bruin/commands/lineage.html), this command visualize your asset dependencies

### Question 7. First-Time Run
> You're running a Bruin pipeline for the first time on a new DuckDB database. What flag should you use to ensure tables are created from scratch?
> - `--create`
> - `--init`
> - `--full-refresh`
> - `--truncate`

**✅ Answer**: <br>
**The answer is `--full-refresh`** 

**Explanation** <br>
To initialize a new environment or apply schema changes to a DuckDB instance, use the `--full-refresh` flag. This ensures all assets are built from the ground up, regardless of their incremental configuration














