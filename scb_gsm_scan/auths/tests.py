from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from auths.models import User
from auths.models import Role, Group
from django_factory_all import ModelFactory
from scb_gsm_scan.utils import login_user_in_test
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

User = get_user_model()

class AuthsTestCase(TestCase):
    def setUp(self):
        self.factory = ModelFactory(max_depth=7, create_m2m=True)
        kwargs_user = self.factory.build_create_kwargs(User)
        self.user = User.objects.create(**kwargs_user)
        self.client = login_user_in_test(self.user)
        
    # test role
        
    def test_create_role_success(self):
        url = reverse('role-list')
        group = self.factory.create(Group)
        response = self.client.post(url, {'name': 'test', 'group': group.id}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertGreaterEqual(Role.objects.count(), 1)
        
    def test_update_role_success(self):
        role = self.factory.create(Role)
        url = reverse('role-detail', kwargs={'pk': role.pk})
        response = self.client.patch(url, {'name': 'test'}, format='json')
        role.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(role.name, 'test')
        
    def test_retrieve_role_success(self):
        role = self.factory.create(Role)
        url = reverse('role-detail', kwargs={'pk': role.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response.data), ReturnDict)
        
    def test_list_role_success(self):
        role = self.factory.create(Role)
        url = reverse('role-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response.data), dict)
         
    def test_delete_role_success(self):
        role = self.factory.create(Role)
        url = reverse('role-detail', kwargs={'pk': role.pk})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Role.objects.filter(pk=role.pk).exists())
        
    # test group 
    
    def test_retieve_group_success(self):
        group = self.factory.create(Group)
        url = reverse('group-detail', kwargs={'pk': group.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response.data), ReturnDict)
        
    def test_retieve_group_failure(self):
        url = reverse('group-detail', kwargs={'pk': "test"})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 404)
        
    def test_list_group_success(self):
        group1 = self.factory.create(Group)
        group2 = self.factory.create(Group)
        url = reverse('group-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, ReturnList)
    
    def test_create_group_failure(self):
        url = reverse('group-list')
        response = self.client.post(url, {'name': 'test'}, format='json')
        self.assertEqual(response.status_code, 405)
        
    def test_update_group_failure(self):
        group = self.factory.create(Group)
        url = reverse('group-detail', kwargs={'pk': group.pk})
        response = self.client.patch(url, {'name': 'test'}, format='json')
        self.assertEqual(response.status_code, 405)
    
    
    # test user
    
    def test_create_user_success(self):
        url = reverse('user-list')
        response = self.client.post(url, {'email': 'testcreate@test.com', 'password': 'test'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertGreaterEqual(User.objects.count(), 1)
    
    def test_create_user_failure(self):
        url = reverse('user-list')
        response = self.client.post(url, {'email': 'test', 'password': 'test'}, format='json')
        self.assertEqual(response.status_code, 400)
    
    def test_update_user_success(self):
        user = User.objects.create(**self.factory.build_create_kwargs(User))
        url = reverse('user-detail', kwargs={'pk': user.pk})
        response = self.client.patch(url, {'email': 'testupdate@test.com'}, format='json')
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.email, 'testupdate@test.com')
        
    def test_update_user_failure(self):
        url = reverse('user-detail', kwargs={'pk': "test"})
        response = self.client.patch(url, {'email': 'testupdate@test.com'}, format='json')
        self.assertEqual(response.status_code, 404)
       
        