# etl_pipeline
Scripts for PharmaDB ETL pipeline

## Running the local set up
1. Build the docker image using `docker-compose build`
2. Start the containers using `docker-compose up`

### Mongo DB
The Mongo database is exposed at `localhost:27017`. The mongo shell can be accessed, to view / manipulate the data, by exec-ing into the container. Local folder `mongo/data` is attached to the DB container using bind mount, to map to the DB's data folder. This retains the data even when the container is removed.

### Mongo Express
Access `localhost:8081` for the Mongo Express viewer, which provides a limited UI to explore the data in the Mongo DB.

### Neo4J DB
Neo4J browser can be accessed via HTTP at `localhost:7474`. Similarly, bolt connection can be established at `localhost:7687`. For more info, refer to the [official docs](https://neo4j.com/docs/operations-manual/current/configuration/connectors/#connectors-available-connectors).

## Clean Up
Run `docker-compose down` to stop and remove all containers.

__NOTE__: The Mongo and Neo4J data should be retained at `./mongo/` and `./neo4j/`, respectively.