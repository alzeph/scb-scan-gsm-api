from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from gsm_coverage.models import GSMData, GSMScan, CSVLine
from django_factory_all import ModelFactory
from scb_gsm_scan.utils import login_user_in_test
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList


User = get_user_model()


class GsmCoverageTestCase(TestCase):

    def setUp(self):
        self.factory = ModelFactory(max_depth=7, create_m2m=True)
        kwargs_user = self.factory.build_create_kwargs(User)
        self.user = User.objects.create(**kwargs_user)
        self.client = login_user_in_test(self.user)
        return super().setUp()

    # test GSM_Data

    def test_create_gsmdata_failure(self):
        url = reverse('gsm_data-list')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 405)

    def test_list_gsmdata_success(self):
        url = reverse('gsm_data-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)

    # test GSMScan

    def test_create_gsmscan_failure(self):
        url = reverse('gsm_scan-list')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_gsmscan_success(self):
        import os
        from django.core.files.uploadedfile import SimpleUploadedFile

        file_path = os.path.join(
            os.path.dirname(__file__), "tests/files", "test.csv")

        # Ouvre le fichier en mode binaire
        with open(file_path, "rb") as f:
            csv_file = SimpleUploadedFile(
                f.name, f.read(), content_type="text/csv")

        # Envoie du fichier au endpoint

        url = reverse('gsm_scan-list')
        response = self.client.post(url, {"file": csv_file, "operator": "TEST"}, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertGreaterEqual(GSMScan.objects.count(), 1)
        
    def test_create_gsmscan_failure(self):
        import os
        from django.core.files.uploadedfile import SimpleUploadedFile

        file_path = os.path.join(
            os.path.dirname(__file__), "tests/files", "test_failure.csv")

        # Ouvre le fichier en mode binaire
        with open(file_path, "rb") as f:
            csv_file = SimpleUploadedFile(
                f.name, f.read(), content_type="text/csv")

        # Envoie du fichier au endpoint

        url = reverse('gsm_scan-list')
        response = self.client.post(url, {"file": csv_file, "operator": "TEST"}, format='multipart')
        self.assertEqual(response.status_code, 400)
 
    def test_update_gsmscan_failure(self):
        url = reverse('gsm_scan-detail', kwargs={'pk': "test"})
        response = self.client.patch(url, {}, format='json')
        self.assertEqual(response.status_code, 404)
        
    def test_update_gsmscan_success(self):
        
        import os
        from django.core.files.uploadedfile import SimpleUploadedFile

        file_path = os.path.join(
            os.path.dirname(__file__), "tests/files", "test.csv")

        # Ouvre le fichier en mode binaire
        with open(file_path, "rb") as f:
            csv_file = SimpleUploadedFile(
                f.name, f.read(), content_type="text/csv")
            
        url = reverse('gsm_scan-list')
        response = self.client.post(url, {"file": csv_file, "operator": "TEST"}, format='multipart')
        url = reverse('gsm_scan-detail', kwargs={'pk': response.data['pk']})
        response = self.client.patch(url, {}, format='json')
        self.assertEqual(response.status_code, 200)
        
    def test_delete_gsmscan_failure(self):
        url = reverse('gsm_scan-detail', kwargs={'pk': "test"})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 405)
    
    # test CSVLine

    def test_create_csvline_failure(self):
        url = reverse('csv_line-list')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 405)
    
    def test_list_csvline_failure(self):
        url = reverse('csv_line-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 405)
        
    def test_delete_csvline_failure(self):
        url = reverse('csv_line-detail', kwargs={'pk': "test"})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 405)
        
    
    def test_update_csvline_failure(self):
        url = reverse('csv_line-detail', kwargs={'pk': "test"})
        response = self.client.patch(url, {}, format='json')
        self.assertEqual(response.status_code, 404)
        
    
    def test_update_csvline_success(self):
        import os
        from django.core.files.uploadedfile import SimpleUploadedFile

        file_path = os.path.join(
            os.path.dirname(__file__), "tests/files", "test.csv")

        # Ouvre le fichier en mode binaire
        with open(file_path, "rb") as f:
            csv_file = SimpleUploadedFile(
                f.name, f.read(), content_type="text/csv")
            
        url = reverse('gsm_scan-list')
        response = self.client.post(url, {"file": csv_file, "operator": "TEST"}, format='multipart')
        if response.data.get('csv_lines') is not None and len(response.data['csv_lines']) > 0:
            data = response.data['csv_lines'][0]
            url = reverse('csv_line-detail', kwargs={'pk': data['pk']})
            response = self.client.patch(url, {}, format='json')
            self.assertEqual(response.status_code, 200)
