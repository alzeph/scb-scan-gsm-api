from rest_framework.test import APIClient
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

def login_user_in_test(user: User) -> APIClient:
    client = APIClient()
    refresh = RefreshToken.for_user(user)

    # Crée le cookie HttpOnly comme le ferait ton backend
    client.cookies["access"] = str(refresh.access_token)
    client.cookies["access"]["httponly"] = True
    client.cookies["access"]["secure"] = True  # si tu testes en HTTPS
    client.cookies["access"]["samesite"] = "None"  # si front séparé

    return client
