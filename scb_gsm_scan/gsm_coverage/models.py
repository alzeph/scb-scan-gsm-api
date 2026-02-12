from django.db import models
from rest_framework import serializers
from django.contrib.auth.models import Group
from scb_gsm_scan.models import TimeStamp


class CSVLine(TimeStamp):
    time = models.DateTimeField(null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    alt = models.FloatField(null=True, blank=True)
    gps_fix = models.PositiveSmallIntegerField(default=3)

    rat = models.CharField(max_length=10)  # GSM / GPRS / EDGE / UMTS / HSPA / LTE / NR
    mccmnc = models.CharField(max_length=10)
    cell_id = models.BigIntegerField(null=True, blank=True)
    
    pci = models.PositiveSmallIntegerField(null=True, blank=True)

    band = models.CharField(max_length=30)
    earfcn = models.PositiveIntegerField(null=True, blank=True)

    rsrp_dbm = models.IntegerField(null=True, blank=True)
    rsrq_db = models.FloatField(null=True, blank=True)
    sinr_db = models.FloatField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["time"]),
            models.Index(fields=["cell_id"]),
            models.Index(fields=["mccmnc"]),
            models.Index(fields=["rat"]),
        ]

    def __str__(self):
        return f"{self.lat} | Cell {self.lon} | {self.alt}"

class GSMScan(TimeStamp):
    file = models.FileField(upload_to='gsm_coverage/csv/')
    csv_lines = models.ManyToManyField(CSVLine)

    def __str__(self):
        return self.file.name


class GSMData(TimeStamp):
    operator = models.OneToOneField(Group, on_delete=models.SET_NULL, null=True, blank=True)
    gsm_scan = models.ManyToManyField(GSMScan)
    
    def __str__(self):
        return self.operator
    
    @classmethod
    def get(cls, operator=None):
        try:
            group, _ = Group.objects.get_or_create(name=operator)
        except:
            serializers.ValidationError(f"Le groupe n'existe pas. {operator} n'a pas puêtre créé.")
        try:
            data, _ = cls.objects.get_or_create(operator=group)
            return data
        except Exception as e:
            print("error : ", e)
            serializers.ValidationError(str(e))
    
    class Meta:
        indexes = [
            models.Index(fields=["operator"]),
        ]
        ordering = ["-created_at"]
    

