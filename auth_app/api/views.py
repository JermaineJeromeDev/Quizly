from auth_app.utils import (
    delete_auth_cookies,
    extract_serializer_error,
    generate_tokens_for_user,
    set_auth_cookies,
)
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import IsCookieAuthenticated
from .serializers import UserLoginSerializer, UserRegisterSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request) -> Response:
    """Registriert einen neuen Benutzer via Serializer."""
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        error_message = extract_serializer_error(serializer.errors)
        return Response({"detail": error_message}, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    return Response(
        {"detail": "User created successfully!"}, status=status.HTTP_201_CREATED
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request) -> Response:
    """Loggt den User ein und setzt die JWT-Cookies (DoD-konform)."""
    serializer = UserLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"detail": "Ungültige Anmeldedaten."}, status=status.HTTP_401_UNAUTHORIZED
        )

    user = authenticate(
        username=serializer.validated_data["username"],
        password=serializer.validated_data["password"],
    )
    if user is None:
        return Response(
            {"detail": "Ungültige Anmeldedaten."}, status=status.HTTP_401_UNAUTHORIZED
        )

    tokens = generate_tokens_for_user(user)
    response = Response(
        {
            "detail": "Login successfully!",
            "user": {"id": user.id, "username": user.username, "email": user.email},
        },
        status=status.HTTP_200_OK,
    )

    set_auth_cookies(response, tokens)
    return response


@api_view(["POST"])
@permission_classes([IsCookieAuthenticated])
def logout_user(request) -> Response:
    """Loggt den User aus, blacklisted das Token und loescht Cookies."""
    refresh_token = request.COOKIES.get("refresh_token")

    if refresh_token:
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            pass

    msg = "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."
    response = Response({"detail": msg}, status=status.HTTP_200_OK)
    delete_auth_cookies(response)
    return response
