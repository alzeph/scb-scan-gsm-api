from django.urls import path, include
from rest_framework.routers import DefaultRouter
from gsm_coverage import views

router = DefaultRouter()

router.register(r'gsm_data', views.GSMDataViewSet, basename='gsm_data')
router.register(r'gsm_scan', views.GSMScanViewSet, basename='gsm_scan')
router.register(r'csv_line', views.CSVLineViewSet, basename='csv_line')

urlpatterns = [
    path('gsm_coverage/', include(router.urls)),
]
