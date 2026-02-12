from rest_framework import viewsets, permissions, mixins
from django.contrib.auth import get_user_model
from auths.models import Role, Group
from auths.serializers import (
    RoleSerializer, GroupSerializer, UserSerializer,
    UserSerializer
)

User = get_user_model()


class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les rôles.
    Seules les méthodes GET, POST, PATCH et DELETE sont autorisées.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']
    

class GroupViewSet(
    mixins.ListModelMixin, 
    mixins.RetrieveModelMixin, 
    viewsets.GenericViewSet
    ):
    """
    ViewSet qui ne permet que GET (liste et détail) sur Group.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']
    



