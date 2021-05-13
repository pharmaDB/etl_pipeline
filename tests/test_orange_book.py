import os
import pytest

from orangebook.orange_book import download_latest_orange_book, parse_csv_data

TEST_DATA_DIR = os.path.join("tests", "testdata")
TEMPDATA_DIR = os.path.join("tests", "tempdata")


@pytest.fixture
def setup_temp_datadir():
    if not os.path.exists(TEMPDATA_DIR):
        os.makedirs(TEMPDATA_DIR)


def test_parse_csv_data():
    nda_patent_list = parse_csv_data(
        os.path.join(TEST_DATA_DIR, "orange_book.csv"), "~"
    )
    assert nda_patent_list == [
        {"nda": "020610", "patent_num": "7625884"},
        {"nda": "020685", "patent_num": "6689761"},
        {"nda": "020685", "patent_num": "6689761"},
        {"nda": "020685", "patent_num": "6689761"},
        {"nda": "020723", "patent_num": "7696159"},
        {"nda": "018613", "patent_num": "7560445"},
    ]


def test_download_latest_orange_book(setup_temp_datadir):
    file_path = os.path.join(TEMPDATA_DIR, "orange_book.zip")
    if os.path.exists(file_path):
        os.remove(file_path)

    download_latest_orange_book(file_path)
    assert os.path.exists(file_path)
    os.remove(file_path)
