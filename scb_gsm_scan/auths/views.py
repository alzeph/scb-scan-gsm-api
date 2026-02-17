from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import viewsets, permissions, mixins, serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from auths.models import Role, Group
from auths.serializers import (
    RoleSerializer, GroupSerializer, UserSerializer,
    UserSerializer
)

User = get_user_model()


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        if not email:
            raise serializers.ValidationError("L'email est obligatoire")
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("L'utilisateur n'existe pas")
        return email


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

    @extend_schema(
        methods=['post'],
        operation_id="get_current_user",
        summary="Get current user",
        description="Get current user",
        responses={200: UserSerializer},
        request=EmailSerializer
    )
    @action(
        detail=False,
        methods=['post'],
        url_name='current',
        url_path=r'current'
    )
    def current_user(self, request):
        request_serializer = EmailSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


@extend_schema(
    summary="Refresh access token via HttpOnly cookie",
    description=(
        "Rafraîchit le token d’accès en utilisant le refresh token "
        "stocké dans un cookie HttpOnly. "
        "Aucun paramètre n’est attendu dans la requête."
    ),
    request=None,
    responses={
        200: OpenApiResponse(
            description="Access token rafraîchi avec succès"
        ),
        401: OpenApiResponse(
            description="Refresh token manquant ou expiré"
        ),
    },
)
class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get("refresh")
        print("refresh =>", refresh)
        print("access =>", request.COOKIES.get("access"))

        if not refresh:
            return Response(
                {"detail": "Refresh token manquant"},
                status=401
            )

        request.data["refresh"] = refresh

        response = super().post(request, *args, **kwargs)

        access = response.data.get("access")

        response.set_cookie(
            key="access",
            value=access,
            httponly=True,
            secure=True,
            samesite=None,
        )

        response.data = {"detail": "token refreshed"}
        return response


@extend_schema(
    summary="Access token via HttpOnly cookie",
    description=(
        "Accès au token d’accès"
    ),
    responses={
        200: OpenApiResponse(
            description="Access token rafraîchi avec succès",
            response=UserSerializer
        ),
        401: OpenApiResponse(
            description="Refresh token manquant ou expiré"
        ),
    },
)
class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        access = response.data.get("access")
        refresh = response.data.get("refresh")

        try:
            user = User.objects.get(email=request.data.get("email"))
            user.last_login = timezone.now()
            user.save()
        except User.DoesNotExist:
            return response({"detail": "User not found"}, status=401)

        response = Response(UserSerializer(user).data)
        response.set_cookie(
            key="access",
            value=access,
            httponly=True,
            secure=True,
            samesite=None,
        )

        response.set_cookie(
            key="refresh",
            value=refresh,
            httponly=True,
            secure=True,
            samesite=None,
        )

        return response


@extend_schema(
    operation_id="session_check",
    summary="Check session",
    description=(
        "Accès au token d’accès"
    ),
    responses={
        200: OpenApiResponse(
            description="Access token rafraîchi avec succès",
            response=UserSerializer
        ),
        401: OpenApiResponse(
            description="Refresh token manquant ou expiré"
        ),
    },
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def session_check(request):
    # Si on arrive ici, le user est authentifié
    return Response(UserSerializer(request.user).data)


@extend_schema(
    summary="Logout",
    operation_id="logout",
    description=(
        "Logout"
    ),
    responses={
        204: OpenApiResponse(
            description="Logout"
        ),
    },
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def logout(request):
    try:
        refresh = request.COOKIES.get("refresh")
        if refresh:
            token = RefreshToken(refresh)
            token.blacklist()
    except Exception:
        pass

    response = Response(status=status.HTTP_204_NO_CONTENT)
    response.delete_cookie("access")
    response.delete_cookie("refresh")
    return response
