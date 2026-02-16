from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from rest_framework import permissions
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
)
from django.urls import path, include
from auths.urls import urlpatterns as urlpatterns_auths
from gsm_coverage.urls import urlpatterns as urlpatterns_gsm

url_app = [
    path('', include(urlpatterns_auths)),
    path('', include(urlpatterns_gsm))
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path("chaining/", include("smart_selects.urls")),
    path('api/', include(url_app)),
]

# decouverte API


# decouverte des fichiers static en developement
if settings.DEBUG:
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view()),
        path('api/schema/swagger-ui/',
             SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('api/schema/redoc/',
             SpectacularRedocView.as_view(url_name='schema'), name='redoc')
    ]
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(
            permission_classes=[permissions.IsAuthenticated]), name='schema'),
    ]
