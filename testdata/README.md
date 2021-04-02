# testdata

This folder contains some test data in JSON format that can be imported directly into a MongoDB instance. Steps are described in detail for generating test data using other drug NDA application numbers.

## Importing the JSON Mongo Dump Data

The data covers drugs: `MORPHINE SULFATE`, `MINOXIDIL`

**Recommended:** Use the docker-compose config in this repo to start up the DB, which is accompanied by the Mongo Express viewer.

The json files include data dumps for the `labels` and `patents` collections, respectively. The `labels` schema is complete, whereas the `patents` currently include only the most critical fields. To import the json data, use the following commands for each collection.

* Copy the JSON file into the Docker container (optional, if the DB runs inside a container).
```
$ docker cp <local_file.json> container_name:.
```

* Import the data (`exec` into the container first, if using Docker).
```
$ docker exec -it container_name sh
$ mongoimport --db <db_name> --collection <collection_name> --file <local_file.json>
```

## Generating Test Data for Other NDA Application Numbers

**NOTE** The `sample_data_EDA_import_mongo.ipynb` notebook at [this repo](https://github.com/pharmaDB/data_analysis/tree/main/ds_notebook/notebooks) contains the supporting code for the steps below.

1. Refer to the [Drug Label set ID to NDA number association](https://github.com/pharmaDB/data_analysis/blob/main/ds_notebook/notebooks/spl_id_label_nda.csv). Select some NDA numbers.
2. Refer to the [Orange Book Association sample data](https://raw.githubusercontent.com/pharmaDB/nber.org-Orange-Book-Data/main/FDA_drug_patents.csv). Use the NDA numbers from step #1 to find the matching patent numbers.
3. Obtain the USPTO [Patent Claim Research dataset](https://developer.uspto.gov/product/patent-and-patent-application-claims-data-stata-dta-and-ms-excel-csv). Check that the claim data exists for the patents from step #2 (this dataset stops at around 2014). The usage of this dataset is a temporary workaround while we finalize the patent data collection.
4. Provide the SPL set IDs linked to the chosen NDAs in step #1, to download and populate historical label data into the configured MongoDB, based on the steps in [this repo](https://github.com/pharmaDB/dailymed_data_processor).
5. Run the last section (patent processing and import) of the notebook `sample_data_EDA_import_mongo.ipynb` at [this repo](https://github.com/pharmaDB/data_analysis/tree/main/ds_notebook/notebooks) to load the patent info into the configured MongoDB instance.
