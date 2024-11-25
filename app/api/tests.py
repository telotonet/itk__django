import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_file_upload_success(client: APIClient, mock_openpyxl):
    url = reverse("file-upload")
    with open("tests/test_data/example.xlsx", "rb") as file:
        response = client.post(url, {"file": file}, format="multipart")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["message"] == "File uploaded and data saved successfully."


@pytest.mark.django_db
def test_file_upload_invalid_format(client: APIClient):
    url = reverse("file-upload")
    with open("tests/test_data/invalid_file.txt", "rb") as file:
        response = client.post(url, {"file": file}, format="multipart")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Unsupported file format" in response.data["error"]


@pytest.mark.django_db
def test_record_list_view(client: APIClient):
    url = reverse("record-list")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)


@pytest.mark.django_db
def test_html_table_view(client: APIClient):
    url = reverse("html-table")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert "table" in response.content.decode()  # Проверяем, что есть таблица в ответе


import pytest

from .utils import validate_header


def test_validate_header():
    header_valid = ["ne", "address", "coordinates", "technology", "status"]
    validate_header(header_valid)  # Не должно вызывать исключений

    header_invalid = ["ne", "address", "coordinates"]
    with pytest.raises(ValueError, match="Missing required columns: status, technology"):
        validate_header(header_invalid)


from .utils import extract_column_indices


def test_extract_column_indices():
    header = ["ne", "address", "coordinates", "technology", "status"]
    column_indices = extract_column_indices(header)

    assert column_indices == {
        "ne": 0,
        "address": 1,
        "coordinates": 2,
        "technology": 3,
        "status": 4,
    }


from .utils import process_row


def test_process_row():
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


import openpyxl

from .utils import parse_excel


@pytest.mark.django_db
def test_parse_excel():
    # Создаем временный файл Excel для теста
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["ne", "address", "coordinates", "technology", "status"])
    ws.append(["NE1", "Address 1", "48.8566, 2.3522", "gsm, lte", 1])

    # Сохраняем файл в временный файл
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
