from rest_framework.test import APIClient
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


def login_user_in_test(user: User) -> APIClient:
    client = APIClient()
    token = RefreshToken.for_user(user)
    auth_header = f"Bearer {token.access_token}"
    client.credentials(HTTP_AUTHORIZATION=auth_header)
    return client