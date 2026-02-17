from rest_framework import viewsets, permissions, mixins
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from gsm_coverage.models import GSMData, GSMScan, CSVLine
from gsm_coverage.serializers import GSMDataSerializer, GSMScanSerializer, CSVLineSerializer
from django_filters.rest_framework import DjangoFilterBackend


class GSMDataViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = GSMData.objects.all()
    serializer_class = GSMDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['operator'] 
    
    
class GSMScanViewSet(viewsets.ModelViewSet):
    queryset = GSMScan.objects.all()
    serializer_class = GSMScanSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'patch']
    

class CSVLineViewSet(viewsets.ModelViewSet):
    queryset = CSVLine.objects.all()
    serializer_class = CSVLineSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch']




