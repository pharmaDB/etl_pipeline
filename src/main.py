from datetime import datetime
import json
import os
import subprocess

from db.mongo import connect_mongo, get_connection_string, MongoClient
from druglabels.drug_labels import (
    download_latest_labels,
    process_label_metadata_and_save_to_mongo,
    get_label_mappings_for_ndas,
)
from orangebook.orange_book import (
    download_latest_orange_book,
    process_orange_book_and_save_to_mongo,
    get_orange_book_mappings_since,
)
from utils.logging import getLogger

_logger = getLogger("main")

TEMP_DATA_FOLDER = "tempdata"

MONGO_DB_PIPELINE_COLLECTION = "pipeline"


def get_latest_pipeline_run_timestamp():
    """This function returns the timestamp of the last successful run of the
    pipeline, or None.

    Returns:
        datetime: The timestamp field from the first (expected to be only) doc
                  in the pipeline collection
    """
    mongo_client = MongoClient(connect_mongo())
    doc = mongo_client.find(MONGO_DB_PIPELINE_COLLECTION, {})
    if not doc.count():
        return None
    return doc[0]["timestamp"]


def set_latest_pipeline_run_timestamp(timestamp):
    mongo_client = MongoClient(connect_mongo())
    mongo_client.upsert(
        MONGO_DB_PIPELINE_COLLECTION, {}, {"timestamp": timestamp}
    )


def write_updated_orange_book_set_ids(file_path, since=None):
    """This function checks the newly added OrangeBook mappings in
        the MongoDB database to identify the updated NDA numbers.
        The corresponding DailyMed set IDs are written to a local file
        so that they can be downloaded and processed by the label processing
        module.

    Args:
        file_path (str): The path at which to write the DailyMed set ID list
                         in json format
        since (datettime): The timestamp to act as "from" filter for the query
    """
    ob_mappings = get_orange_book_mappings_since(since=since)
    label_mappings = get_label_mappings_for_ndas(
        ndas=list(map(lambda x: x["nda"], ob_mappings))
    )
    set_ids = list(set(map(lambda x: x["set_id"], label_mappings)))
    with open(file_path, "w+") as f:
        f.write(json.dumps(set_ids))


if __name__ == "__main__":
    started_time = datetime.now()

    # Create temp data folder if not exists
    if not os.path.exists(TEMP_DATA_FOLDER):
        os.mkdir(TEMP_DATA_FOLDER)

    # Download Latest Orange Book
    orange_book_zip_path = os.path.join(TEMP_DATA_FOLDER, "orange_book.zip")
    download_latest_orange_book(file_path=orange_book_zip_path)

    # Process Orange Book and save to MongoDB
    process_orange_book_and_save_to_mongo(
        file_path=orange_book_zip_path,
        destination_folder_path=os.path.join(
            TEMP_DATA_FOLDER, "orange_book_data"
        ),
    )

    # Download the latest Drug Labels
    drug_labels_zip_path = os.path.join(TEMP_DATA_FOLDER, "drug_labels.zip")
    download_latest_labels(file_path=drug_labels_zip_path)

    # Process the latest Drug Labels archive to get the NDA -> Set ID map
    # and save to MongoDB
    process_label_metadata_and_save_to_mongo(
        file_path=drug_labels_zip_path,
        destination_folder_path=os.path.join(
            TEMP_DATA_FOLDER, "drug_labels_data"
        ),
    )

    # Output the Set IDs corresponding to the new Orange Book mappings
    # into a local file, for processing in the subsequent steps.
    setid_file_path = os.path.join(TEMP_DATA_FOLDER, "set_ids.json")
    write_updated_orange_book_set_ids(
        setid_file_path, since=get_latest_pipeline_run_timestamp()
    )

    # Download the label data
    subprocess.call(
        [
            "python3",
            "submodules/dailymed_data_processor/main.py",
            f"--set_ids_from_file={setid_file_path}",
        ]
    )

    # Download the patent data
    start_date = started_time.strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    conn_string = get_connection_string()
    subprocess.call(
        [
            "node",
            "submodules/uspto_bulk_file_processor_v4/out/index.js",
            "--patent-number-file=patents.json",
            f"--start-date={start_date}",
            f"--end-date={end_date}",
            f"--connection-string={conn_string}",
        ]
    )

    # Run scoring data processor on the new data
    subprocess.call(["python3", "submodules/scoring_data_processor/main.py"])

    # Export the results of the scoring
    subprocess.call(
        ["python3", "submodules/scoring_data_processor/main.py", "-db2csv"]
    )

    # Update the latest run timestamp to the MongoDB pipeline collection
    set_latest_pipeline_run_timestamp(started_time)
