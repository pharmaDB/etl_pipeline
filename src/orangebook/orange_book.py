from bs4 import BeautifulSoup as bs
import csv
from datetime import datetime
import os
import requests
import re
import shutil
import zipfile

from db.mongo import connect_mongo, MongoClient
from utils.logging import getLogger

_logger = getLogger(__name__)

BASE_URL = "https://www.fda.gov"
MONGO_COLLECTION_NAME = "orangebook"


def download_latest_orange_book(file_path):
    """This function downloads the latest Orange Book data from the FDA website,
    using the URL provided under "Orange Book Data Files (compressed)", at:
    https://www.fda.gov/drugs/drug-approvals-and-databases/orange-book-data-files

    It is expected that the URL that holds the latest Orange Book data changes
    from time to time. Thus, this is obtained dynamically.

    Args:
        file_path (str): The expected file path where the downloaded Orange Book
                         zip file should be placed
    """

    url = (
        f"{BASE_URL}/drugs/drug-approvals-and-databases/orange-book-data-files"
    )
    r = requests.get(url, allow_redirects=True)
    page_data = None
    try:
        page_data = r.text
    except Exception as e:
        _logger.error(f"Unable to access FDA's Orange Book resources URL")

    # Get the latest Orange Book supplement's URL
    bs_content = bs(page_data, "lxml")
    supplement_download_url = None
    for link in bs_content.findAll("a"):
        if link.string == "Orange Book Data Files (compressed)":
            supplement_download_url = BASE_URL + link["href"]
            break

    # Download the data to the given path
    _logger.info(f"Downloading the Orange Book data into {file_path}")
    r = requests.get(supplement_download_url, allow_redirects=True)
    with open(file_path, "wb+") as f:
        f.write(r.content)


def parse_csv_data(file_path, sep=","):
    """Parses the NDA number and patent associations in the given file.

    Args:
        file_path (str): Path to the Orange Book patent data
        sep (str, optional): The separator used in the Orange Book patent data.
                             Defaults to ",".

    Returns:
        list(dict): Each object contains fields 'nda' and 'patent_num'
    """
    nda_patent_list = []
    with open(file_path) as csvfile:
        data_reader = csv.DictReader(csvfile, delimiter=sep)
        for row in data_reader:
            if row["Appl_Type"] == "N":
                # Keep only the numbers in the patents
                nda_patent_list.append(
                    {
                        "nda": row["Appl_No"],
                        "patent_num": re.sub("[^0-9]+", "", row["Patent_No"]),
                    }
                )
    return nda_patent_list


def save_orange_book_data(rows):
    mongo_client = MongoClient(connect_mongo())
    new_records_count = 0

    for row in rows:
        # Find doc in MongoDB
        doc = mongo_client.find(
            MONGO_COLLECTION_NAME,
            row,
        )
        if not doc.count():
            new_records_count += 1
            mongo_client.insert(
                MONGO_COLLECTION_NAME, {**row, "created_at": datetime.now()}
            )
    _logger.info(f"Inserted {new_records_count} new Orange Book associations")


def process_orange_book_and_save_to_mongo(file_path, destination_folder_path):
    """Processes the downloaded Orange Book zip file, saving the
    NDA -> Patent number mappings to MongoDB.

    Args:
        file_path (str): The path at which the downloaded Orange Book
                         zip file is placed
        destination_folder_path (str): The path at which the Orange Book
                                       zip should be extracted
    """
    # Check input data
    if not os.path.exists(file_path):
        _logger.error("Zip File containing latest Orange Book data not found")
        return

    # Create the folder to extract the contents into, if not exists
    if not os.path.exists(destination_folder_path):
        os.mkdir(destination_folder_path)

    # Extract zip file's contents
    _logger.info(
        f"Extracting the Orange Book data into {destination_folder_path}"
    )
    try:
        with zipfile.ZipFile(file_path, "r") as zip_obj:
            zip_obj.extractall(destination_folder_path)
    except Exception as e:
        _logger.error(f"Unable to extract zip file {file_path}: {e}")
        return

    # Parse the patents CSV data
    orange_book_rows = parse_csv_data(
        os.path.join(destination_folder_path, "patent.txt"), sep="~"
    )
    _logger.info(
        f"Found {len(orange_book_rows)} associations in the Orange Book file"
    )

    # Save to MongoDB
    save_orange_book_data(orange_book_rows)

    # Delete the extracted files and the original zip file
    shutil.rmtree(destination_folder_path)
    os.remove(file_path)
