from django.urls import path, include
from rest_framework.routers import DefaultRouter
from auths import views

router = DefaultRouter()

router.register(r'roles', views.RoleViewSet, basename='role')
router.register(r'groups', views.GroupViewSet, basename='group')
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    path('auths/', include(router.urls)),
]
