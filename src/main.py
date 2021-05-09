import os

from druglabels.drug_labels import (
    download_latest_labels,
    process_label_metadata_and_save_to_mongo,
)
from orangebook.orange_book import (
    download_latest_orange_book,
    process_orange_book_and_save_to_mongo,
)
from utils.logging import getLogger

_logger = getLogger("main")

TEMP_DATA_FOLDER = "tempdata"

if __name__ == "__main__":
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
