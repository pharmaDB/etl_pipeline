from bs4 import BeautifulSoup as bs
from contextlib import closing
from datetime import datetime, timedelta

import concurrent.futures
import os
import shutil
import urllib.request as request
import zipfile

from db.mongo import connect_mongo, MongoClient
from utils.logging import getLogger

_logger = getLogger(__name__)

_mongo_client = MongoClient(connect_mongo())
MONGO_COLLECTION_NAME = "labelmap"


def download_latest_labels(file_path):
    """This function downloads the latest drug labels monthly archive file
    from Dailymed, at the URL of the format:
    ftp://public.nlm.nih.gov/nlmdata/.dailymed/dm_spl_monthly_update_{month}{year}.zip

    Args:
        file_path (str): The path at which the archive file should be downloaded
    """
    # Get the date as of the last month
    now = datetime.now()
    prev_month_lastday = now.replace(day=1) - timedelta(days=1)
    month, year = (
        prev_month_lastday.strftime("%b").lower(),
        prev_month_lastday.year,
    )
    archive_url = f"ftp://public.nlm.nih.gov/nlmdata/.dailymed/dm_spl_monthly_update_{month}{year}.zip"

    # Download the drug labels archive file
    with closing(request.urlopen(archive_url)) as r:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(r, f)


def process_nda_set_id_mapping(zip_file_path):
    # Define method to extract the NDA number(s) from the XML data
    def get_application_numbers_from_label_xml(set_id, bs_content):
        application_numbers = set()
        try:
            components = bs_content.document.component.structuredbody.component
            for item in components.find_all("approval"):
                if hasattr(item, "code") and item.code["displayname"] == "NDA":
                    # Capture the corresponding NDA number, without the "NDA" prefix and
                    # without leading zeros
                    appln_num = (
                        item.id["extension"][3:]
                        if item.id["extension"].startswith("NDA")
                        else item.id["extension"]
                    )
                    application_numbers.add(str(int(appln_num)))
        except Exception as e:
            _logger.error(
                f"Error in get_application_numbers for set ID {set_id}: {e}"
            )
        return list(application_numbers)

    # Define method to insert to MongoDB
    def save_to_mongo(set_id, application_numbers):
        for appln_number in application_numbers:
            find_by = {"set_id": set_id, "nda": appln_number}
            doc = _mongo_client.find(
                MONGO_COLLECTION_NAME,
                find_by,
            )
            if not doc.count():
                _mongo_client.insert(
                    MONGO_COLLECTION_NAME,
                    {**find_by, "created_at": datetime.now()},
                )
            _logger.info(f"Inserted labelmap associations for set id {set_id}")

    # Extract file contents
    folder_path = zip_file_path[:-4]
    try:
        with zipfile.ZipFile(zip_file_path, "r") as zip_obj:
            zip_obj.extractall(folder_path)
    except Exception as e:
        _logger.error(f"Unable to extract zip file {zip_file_path}: {e}")
        return

    # Parse the XML file
    for dir_name, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith(".xml"):
                with open(os.path.join(dir_name, file_name)) as f:
                    # Init BeautifulSoup object with the contents
                    bs_content = bs(f.read(), "lxml")
                    # Get Set ID
                    set_id = bs_content.document.setid["root"]
                    # Get Application Numbers
                    application_numbers = (
                        get_application_numbers_from_label_xml(
                            set_id, bs_content
                        )
                    )

                # Insert into MongoDB
                if application_numbers:
                    save_to_mongo(set_id, application_numbers)


def process_label_metadata_and_save_to_mongo(
    file_path, destination_folder_path
):
    """Processes the downloaded Labels zip file, saving the
    NDA -> DailyMed SetID mappings to MongoDB.

    Args:
        file_path (str): The path at which the downloaded DailyMed archive
                         zip file is placed
        destination_folder_path (str): The path at which the DailyMed label
                                       zip should be extracted
    """
    # Check input data
    if not os.path.exists(file_path):
        _logger.error(
            "Zip File containing latest DailyMed label data not found"
        )
        return

    # Create the folder to extract the contents into, if not exists
    if not os.path.exists(destination_folder_path):
        os.mkdir(destination_folder_path)

    # Extract zip file's contents
    _logger.info(
        f"Extracting the Drug Label data into {destination_folder_path}"
    )
    try:
        with zipfile.ZipFile(file_path, "r") as zip_obj:
            zip_obj.extractall(destination_folder_path)
    except Exception as e:
        _logger.error(f"Unable to extract zip file {file_path}: {e}")
        return

    # Extract nested files' contents, check for nda mapping and save to DB
    zip_files = []
    for dir_name, _, files in os.walk(destination_folder_path):
        for file_name in files:
            if file_name.endswith(".zip"):
                zip_files.append(os.path.join(dir_name, file_name))

    # Process in parallel
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for zip_file_path, _ in zip(
            zip_files,
            executor.map(
                process_nda_set_id_mapping,
                zip_files,
            ),
        ):
            _logger.info(f"Processed label zip: {zip_file_path}")

    # Delete all downloaded data
    shutil.rmtree(destination_folder_path)
    os.remove(file_path)