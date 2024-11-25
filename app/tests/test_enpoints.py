"""
This module contains test cases for validating API endpoints and utility functions
related to file uploads, data processing, and database interactions.
The tests ensure proper functionality of features such as file upload, data validation,
record retrieval, and HTML table rendering.
"""

import openpyxl
import pytest
from api.utils import extract_column_indices, parse_excel, process_row, validate_header
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_file_upload_success(client: APIClient):
    """
    Test successful file upload.
    Ensures the endpoint handles valid Excel files correctly.
    """
    url = reverse("file-upload")
    with open("tests/test_data/test_file.xlsx", "rb") as file:
        response = client.post(url, {"file": file}, format="multipart")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["message"] == "File uploaded and data saved successfully."


@pytest.mark.django_db
def test_file_upload_invalid_format(client: APIClient):
    """
    Test file upload with an invalid file format.
    Ensures the endpoint rejects unsupported file types.
    """
    url = reverse("file-upload")
    with open("tests/test_data/invalid_file.txt", "rb") as file:
        response = client.post(url, {"file": file}, format="multipart")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Unsupported file format" in response.data["error"]


@pytest.mark.django_db
def test_record_list_view(client: APIClient):
    """
    Test the record list view.
    Ensures the endpoint returns a list of records.
    """
    url = reverse("record-list")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)


@pytest.mark.django_db
def test_html_table_view(client: APIClient):
    """
    Test the HTML table view.
    Ensures the endpoint returns HTML content with a table.
    """
    url = reverse("html-table")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert "table" in response.content.decode()


def test_validate_header():
    """
    Test the header validation function.
    Ensures the function raises an error for missing columns and passes for valid headers.
    """
    header_valid = ["ne", "address", "coordinates", "technology", "status"]
    validate_header(header_valid)

    header_invalid = ["ne", "address", "coordinates"]
    with pytest.raises(ValueError):
        validate_header(header_invalid)


def test_extract_column_indices():
    """
    Test the column index extraction function.
    Ensures it correctly maps column names to their respective indices.
    """
    header = ["ne", "address", "coordinates", "technology", "status"]
    column_indices = extract_column_indices(header)

    assert column_indices == {
        "ne": 0,
        "address": 1,
        "coordinates": 2,
        "technology": 3,
        "status": 4,
    }


def test_process_row():
    """
    Test the row processing function.
    Ensures it correctly processes a row and extracts relevant data.
    """
    row = ["NE1", "Address 1", "48.8566, 2.3522", "gsm, lte", 1]
    column_indices = {
        "ne": 0,
        "address": 1,
        "coordinates": 2,
        "technology": 3,
        "status": 4,
    }
    result = process_row(row, column_indices)
    assert result == {
        "ne": "NE1",
        "address": "Address 1",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "gsm": True,
        "umts": False,
        "lte": True,
        "status": 1,
    }


@pytest.mark.django_db
def test_parse_excel():
    """
    Test the Excel parsing function.
    Ensures it processes an Excel file and extracts records into a structured format.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["ne", "address", "coordinates", "technology", "status"])
    ws.append(["NE1", "Address 1", "48.8566, 2.3522", "gsm, lte", 1])

    file_path = "tests/test_data/test_file.xlsx"
    wb.save(file_path)

    with open(file_path, "rb") as file:
        records = parse_excel(file)

    assert len(records) == 1
    assert records[0]["ne"] == "NE1"
    assert records[0]["latitude"] == 48.8566
    assert records[0]["longitude"] == 2.3522
    assert records[0]["gsm"] is True
    assert records[0]["lte"] is True
    assert records[0]["status"] == 1
