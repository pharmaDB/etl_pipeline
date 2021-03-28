# etl_pipeline
Scripts for PharmaDB ETL pipeline

## Running the local set up
1. Build the docker image using `docker-compose build`
2. Start the containers using `docker-compose up`

### Mongo DB
The Mongo database is exposed at `localhost:27017`. The mongo shell can be accessed, to view / manipulate the data, by exec-ing into the container. Local folder `mongo/data` is attached to the DB container using bind mount, to map to the DB's data folder. This retains the data even when the container is removed.

### Mongo Express
Access `localhost:8081` for the Mongo Express viewer, which provides a limited UI to explore the data in the Mongo DB.

## Clean Up
Run `docker-compose down`