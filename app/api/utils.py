"""
utils.py

Utility module for handling Excel file parsing in a Django-based API.
Provides functionality for parsing Excel files, validating column structure, 
and transforming data into a format suitable for database insertion.

Functions:
    parse_excel(file): Main function for parsing an Excel file.
    validate_header(header): Validates the presence of required columns in the header.
    extract_column_indices(header): Extracts column indices for required columns.
    process_row(row, column_indices): Processes a single row and extracts the necessary data.
"""

import openpyxl

REQUIRED_COLUMNS = {
    "ne",
    "address",
    "coordinates",
    "technology",
    "status",
}


def validate_header(header):
    """
    Validates that the header contains all required columns.

    Args:
        header (list): A list of column names from the Excel header row.

    Raises:
        ValueError: If required columns are missing.
    """
    if not REQUIRED_COLUMNS.issubset(set(header)):
        missing_columns = REQUIRED_COLUMNS - set(header)
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")


def extract_column_indices(header):
    """
    Extracts column indices for required columns based on the header.

    Args:
        header (list): A list of column names from the Excel header row.

    Returns:
        dict: A dictionary mapping column names to their respective indices.
    """
    return {col: header.index(col) for col in REQUIRED_COLUMNS}


def process_row(row, column_indices):
    """
    Processes a single row of data, extracting and validating required fields.

    Args:
        row (tuple): A tuple of cell values for the row.
        column_indices (dict): A dictionary mapping column names to their indices.

    Returns:
        dict: A dictionary containing processed data for the row.

    Raises:
        ValueError: If data in the row is invalid.
    """
    try:
        coordinates = row[column_indices["coordinates"]].split(",")
        latitude = float(coordinates[0].strip())
        longitude = float(coordinates[1].strip())

        technologies = (
            row[column_indices["technology"]].split(",")
            if row[column_indices["technology"]]
            else []
        )
        gsm = "gsm" in [tech.strip().lower() for tech in technologies]
        umts = "umts" in [tech.strip().lower() for tech in technologies]
        lte = "lte" in [tech.strip().lower() for tech in technologies]

        return {
            "ne": row[column_indices["ne"]],
            "address": row[column_indices["address"]],
            "latitude": latitude,
            "longitude": longitude,
            "gsm": gsm,
            "umts": umts,
            "lte": lte,
            "status": int(row[column_indices["status"]]),
        }
    except (ValueError, AttributeError, IndexError) as e:
        raise ValueError(f"Error processing row: {row} — {e}")


def parse_excel(file):
    """
    Parses an Excel file to extract required data for database insertion.
    Validates the presence of required columns and handles missing or invalid data.

    Args:
        file (File): An Excel file object to be parsed.

    Returns:
        list[dict]: A list of dictionaries containing parsed and validated records.

    Raises:
        ValueError: If required columns are missing, or rows contain invalid data.
        openpyxl.utils.exceptions.InvalidFileException: If the file is not a valid Excel file.
    """
    try:
        wb = openpyxl.load_workbook(file)
        sheet = wb.active

        header = [cell.value for cell in sheet[1]]
        validate_header(header)
        column_indices = extract_column_indices(header)

        records = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            records.append(process_row(row, column_indices))

        return records

    except openpyxl.utils.exceptions.InvalidFileException:
        raise ValueError("The uploaded file is not a valid or supported Excel file.")
