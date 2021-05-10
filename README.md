# etl_pipeline
Scripts for PharmaDB ETL pipeline

## Running the local set up
1. Build the docker image using `docker-compose build`
2. Start the containers using `docker-compose up`

### Mongo DB
The Mongo database is exposed at `localhost:27017`. The mongo shell can be accessed, to view / manipulate the data, by exec-ing into the container. Local folder `mongo/data` is attached to the DB container using bind mount, to map to the DB's data folder. This retains the data even when the container is removed.

### Mongo Express
Access `localhost:8081` for the Mongo Express viewer, which provides a limited UI to explore the data in the Mongo DB.

### Clean Up
Run `docker-compose down` to stop and remove all containers.

__NOTE__: The Mongo data should be retained at `./mongo/`.

## Periodic Pipeline

### Running the Periodic Pipeline

The script `src/main.py` contains all the logic for periodically retrieving data from the respective data sources and updating the MongoDB database. The following are the steps to be taken.
1. Clone this repo, with the submodules
```
$ git clone --recurse-submodules https://github.com/pharmaDB/etl_pipeline.git
```
2. If the MongoDB server is not on localhost, update the `.env` files in the root of this repo and each of the submodules.
3. Run the pipeline script using `python3 main.py`
4. The script can be run monthly, as a cron job. Eg: `0 0 1 * * python3 main.py`. This can be saved to the cron file using `crontab -e`.

### Pipeline Methodology

TBD
