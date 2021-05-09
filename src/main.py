import os

from orangebook.orange_book import (
    download_latest_orange_book,
    process_and_save_to_mongo,
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
    process_and_save_to_mongo(
        file_path=orange_book_zip_path,
        destination_folder_path=os.path.join(
            TEMP_DATA_FOLDER, "orange_book_data"
        ),
    )
