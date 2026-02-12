from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from rest_framework import serializers
from auths.models import Role


User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=False, write_only=True)
    class Meta:
        model = Role
        fields = ['pk', 'name', 'group']
        extra_kwargs = {
            'pk': {'read_only': True},
        }

class GroupSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)
    class Meta:
        model = Group
        fields = ['pk', 'name', 'permissions', 'roles']
        
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['pk', 'name', 'content_type', 'codename']

class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    user_permissions = PermissionSerializer(many=True, read_only=True)
    class Meta:
        model = User
        fields = [
            'pk', 'email', 'password', 'first_name', 'last_name',  'roles',
            'groups', 'user_permissions', 'date_joined', 'is_active'
            ]
        extra_kwargs = {
            'pk': {'read_only': True},
            'password': {'write_only': True},
            'first_name': {'required': False,},
            'last_name': {'required': False},
            'roles': {'read_only': False},
            'date_joined': {"required":False, 'read_only': False},
            'is_active': {'read_only': False},
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user



