from django.urls import path, include
from rest_framework.routers import DefaultRouter
from auths import views

router = DefaultRouter()

router.register(r'roles', views.RoleViewSet, basename='role')
router.register(r'groups', views.GroupViewSet, basename='group')
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    path('auths/', include(router.urls)),
    path('auths/token/', views.CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auths/token/refresh/', views.CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('auths/session-check/', views.session_check, name='session_check'),
]
