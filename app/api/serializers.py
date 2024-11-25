from rest_framework import serializers

from .models import Record


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = [
            "ne",
            "address",
            "latitude",
            "longitude",
            "gsm",
            "umts",
            "lte",
            "status",
        ]
