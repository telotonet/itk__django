import os

from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Record
from .serializers import FileUploadSerializer, RecordSerializer
from .utils import parse_excel


class FileUploadView(APIView):
    """
    Handles Excel file uploads for saving data to the database.

    Methods:
        post(request): Processes the uploaded Excel file, validates data, and saves records to the database.
    """

    parser_classes = [MultiPartParser]

    SUPPORTED_EXTENSIONS = {".xlsx", ".xlsm", ".xltx"}

    @swagger_auto_schema(
        operation_description="Uploads an Excel file to save data to the database.",
        manual_parameters=[
            openapi.Parameter(
                "file",
                openapi.IN_FORM,
                description="Upload an Excel file (example.xlsx, .xlsm, .xltx).",
                type=openapi.TYPE_FILE,
                required=True,
            )
        ],
        responses={
            201: openapi.Response(
                description="File successfully processed, and data saved.",
                examples={
                    "application/json": {
                        "message": "File uploaded and data saved successfully."
                    }
                },
            ),
            400: openapi.Response(
                description="File processing error.",
                examples={
                    "application/json": {
                        "error": "Invalid file format or processing error."
                    }
                },
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        """
        Handles the POST request to upload and process an Excel file.

        Args:
            request (Request): The HTTP request containing the uploaded file.

        Returns:
            Response: Success or error message based on the processing result.
        """
        serializer = FileUploadSerializer(data=request.data)

        if serializer.is_valid():
            file = serializer.validated_data["file"]

            file_extension = os.path.splitext(file.name)[1].lower()
            if file_extension not in self.SUPPORTED_EXTENSIONS:
                return Response(
                    {
                        "error": "Unsupported file format"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                records = parse_excel(file)
                Record.objects.bulk_create([Record(**record) for record in records])

                return Response(
                    {"message": "File uploaded and data saved successfully."},
                    status=status.HTTP_201_CREATED,
                )
            except ValueError as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecordListView(ListAPIView):
    """
    Retrieves all records from the database and returns them as JSON.

    Attributes:
        queryset: Queryset of all records in the database.
        serializer_class: Serializer class for serializing the records.
    """

    queryset = Record.objects.all()
    serializer_class = RecordSerializer

    @swagger_auto_schema(
        operation_description="Retrieves all records in JSON format.",
        responses={
            200: openapi.Response(
                description="A list of records.",
            )
        },
    )
    def get(self, request, *args, **kwargs):
        """
        Handles the GET request to retrieve all records in JSON format.

        Args:
            request (Request): The HTTP request.

        Returns:
            Response: A list of serialized records in JSON format.
        """
        return super().get(request, *args, **kwargs)


class HTMLTableView(APIView):
    """
    Renders the database records as an HTML table.

    Methods:
        get(request): Retrieves records from the database and renders them as an HTML table.
    """

    @swagger_auto_schema(
        operation_description="Renders records as an HTML table.",
        responses={
            200: openapi.Response(
                description="HTML page displaying records.",
                content={"text/html": {}},
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        """
        Handles the GET request to render records in an HTML table format.

        Args:
            request (Request): The HTTP request.

        Returns:
            HttpResponse: A rendered HTML page displaying the records.
        """
        records = Record.objects.all()
        return render(request, "table.html", {"records": records})
