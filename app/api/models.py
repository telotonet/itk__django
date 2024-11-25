from django.db import models


class Record(models.Model):
    ne = models.CharField(max_length=255)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    gsm = models.BooleanField(default=False)
    umts = models.BooleanField(default=False)
    lte = models.BooleanField(default=False)
    status = models.CharField(max_length=50)
