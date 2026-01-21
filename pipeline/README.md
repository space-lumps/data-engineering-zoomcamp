# SETUP INSTRUCTIONS

### start docker container
```bash
docker build -t test:pandas .
docker run -it --rm test:pandas 12
```

### start postgres
```bash
docker run -it --rm \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql \
  -p 5432:5432 \
  postgres:18
```

### open new terminal and access instance of postgres
navigate to pipeline/
install dev dependencies (ONLY for development)
```bash
uv add --dev pgcli`
```
-- this will add this dependency to pyproject.toml

### tell pgcli how to connect to postgres:
```bash
uv run pgcli -h localhost -p 5432 -u root -d ny_taxi
```
then enter password

## Inside Postgres:
-- list tables:
`\dt `

-- create a test table:
```SQL
CREATE TABLE test (id INTEGER, name VARCHAR(50))
```

-- Insert data
`INSERT INTO test VALUES (1, 'Hello Docker');`

-- Query data
`SELECT * FROM test;`

-- Exit
`\q`
-- even after exiting, the data should still be here


## Now we want to put NYC taxi data into Postgres
### And for this we need an interactive environment

```bash
uv add --dev jupyter
uv run jupyter notebook
```
-- open in browser
-- then, grab token from the terminal as password
-- create a new notebook

## inside the notebook:
```Python
import pandas as pd

# Read a sample of the data
prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow'
url = f'{prefix}/yellow_tripdata_2021-01.csv.gz'
df = pd.read_csv(url)

# Display first rows
df.head()

# Check data types
df.dtypes

# Check data shape
df.shape
```

-- initially the data types are incorrect bc they are not embedded in a CSV and pandas is "guessing"
-- so we need to specify types using a dictionary:
```Python
dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]

df = pd.read_csv(
    url,
    dtype=dtype,
    parse_dates=parse_dates
)
```

### then, to inspect types:
```Python
df['tpep_pickup_datetime']
```

### now we want to put this data inside Postgres:
#### first, install SQLAlchemy
```bash
!uv add sqlalchemy 
!uv add psychopg2-binary
```
-- use this ! notation to use bash command inside Jupyter notebook
-- this will add this dependency to pyproject.toml

```Python
from sqlalchemy import create_engine
engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')
```
now, we can use ```df.to_sql()``` to insert data into database

### now, we get the schema:
```Python
df.head(0).to_sql(name='yellow_taxi_data', con=engine, if_exists='replace')
```

add this on line before to use the schema just returned to create a table:
```Python
df.head(n=0).to_sql(name='yellow_taxi_data', con=engine, if_exists='replace')
```

### check that table has been created:
back in pgcli terminal:
`\dt`

```text
Should see this:
+--------+------------------+-------+-------+
| Schema | Name             | Type  | Owner |
|--------+------------------+-------+-------|
| public | yellow_taxi_data | table | root  |
+--------+------------------+-------+-------+
```

### once we confirm the table was created, we can start inserting data:
-- it is too big to insert data at once, so we must split it into smaller CHUNKS:
```Python
df_iter = pd.read_csv(
    url,
    dtype=dtype,
    parse_dates=parse_dates,
    iterator=True,
    chunksize=100000
)
```

### now we want to add data to the table using these chunks:
--to see progress, first install tqdm:
```!uv add tqdm```
```Python
from tqdm.auto import tqdm
```

then,
```Python
for df_chunk in tqdm(df_iter): 
    # wrapping df_iter inside of tqdm() allows us to see progress as the data is being added
    df_chunk.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')
```
then wait for data to load

### once data is loaded, convert notebook into a script:
```uv run jupyter nbconvert --to=script docker_postgres.ipynb```
(renamed file to ingest_data.py)
and add variables to script file for year and month, then replace these values in url with the variable names... also parameterize as much as possible: pg_user, pg_pass, pg_host, pg_db, pg_port....

### now, make it configurable thru CLI:
We will use click to parse the arguments so we can pass them thru CLI.
```Python
import click
...

@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL username')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default='5432', help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--year', default=2021, type=int, help='Year of the data')
@click.option('--month', default=1, type=int, help='Month of the data')
@click.option('--chunksize', default=100000, type=int, help='Chunk size for ingestion')
@click.option('--target-table', default='yellow_taxi_data', help='Target table name')
def main(pg_user, pg_pass, pg_host, pg_port, pg_db, year, month, chunksize, target_table):
    ...
```

```uv run python ingest_data.py --help```
this command will list the arguments available



### Sample ingestion script for VIRTUAL ENVIRON:
```bash
uv run python ingest_data.py \
  --pg-user=root \
  --pg-pass=root \
  --pg-host=localhost \
  --pg-port=5432 \
  --pg-db=ny_taxi \
  --target-table=yellow_taxi_trips_2021_01 \
  --year=2021 \
  --month=1 \
  --chunksize=100000
  ```

---





# Now, turn it all into a Dockerized pipeline
first, go to Dockerfile:
instead of `COPY pipeline.py .` change to `COPY ingest_data.py`

### Sample ingestion script FOR DOCKER:
```bash
# `uv run python ingest_data.py \` <--- instead of this:
docker run -it --rm \
taxi_ingest:v001 \
  --pg-user=root \
  --pg-pass=root \
  --pg-host=localhost \
  --pg-port=5432 \
  --pg-db=ny_taxi \
  --target-table=yellow_taxi_trips_2021_02 \
  --year=2021 \
  --month=1 \
  --chunksize=100000
  ```


### now, running this throws an error saying there is no container running at localhost
the problem is that localhost inside virtual environment (postgres) is diff from localhost inside Docker container
so, we have to run two containers on the same network
next, run `docker network`
then, `docker network create pg-network` -- this adds a virtual Docker network called pg-network
when we do this, now we can add to ingestion script: `--network=pg-network \`  # add this line

### next, we will stop both running containers are re-run them using the network config:
```bash
# Run PostgreSQL on the network
docker run -it --rm \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql \
  -p 5432:5432 \
  --network=pg-network \
  --name pgdatabase \   # this name is important so the containers can see each other
  postgres:18
```

```bash
docker run -it --rm \
--network=pg-network \
taxi_ingest:v001 \
  --pg-user=root \
  --pg-pass=root \
  --pg-host=pgdatabase \
  --pg-port=5432 \
  --pg-db=ny_taxi \
  --target-table=yellow_taxi_trips_2021_1 \
  --chunksize=100000
```

### next, instead of using pgcli to interact with the tables,
we will use pgadmin-- so, run this in a new terminal:
```bash
# In another terminal, run pgAdmin on the same network
docker run -it --rm \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -v pgadmin_data:/var/lib/pgadmin \
  -p 8085:80 \
  --network=pg-network \
  --name pgadmin \
  dpage/pgadmin4
  ```

### once both are running, open port 8085 in browser and log in to pgadmin using pgadmin credentials
![pgadmin_screenshot](image.png)
here we want to run both ingestion scripts simultaneously using docker compose
create file called docker-compose.yaml
used AI to generate .yaml from our two ingestion scripts:
```yaml
services:
  pgdatabase:
    image: postgres:18
    environment:
      - POSTGRES_USER=root
      - POSTGRES_PASSWORD=root
      - POSTGRES_DB=ny_taxi
    volumes:
      - "ny_taxi_postgres_data:/var/lib/postgresql:rw"
    ports:
      - "5432:5432"
  pgadmin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com
      - PGADMIN_DEFAULT_PASSWORD=root
    volumes:
      - "pgadmin_data:/var/lib/pgadmin"
    ports:
      - "8085:80"

volumes:
  ny_taxi_postgres_data:
  pgadmin_data:
```

### again open port on browser and log in to pgadmin
name: pgdatabase
host: pgdatabase
username: root
password: root

it is running but we have no tables here.
back in terminal run `docker network ls` to see list of running networks
the most recent is called pipeline_default ({folder name}_default)

so , now we want to run this script:
```bash
docker run -it --rm \
--network=pipeline_default \
taxi_ingest:v001 \
  --pg-user=root \
  --pg-pass=root \
  --pg-host=pgdatabase \
  --pg-port=5432 \
  --pg-db=ny_taxi \
  --target-table=yellow_taxi_trips_2021_1 \
  --chunksize=100000
  ```
and we can run this here in terminal
and then refresh tables inside of pgadmin and the table will be here filled with our data!