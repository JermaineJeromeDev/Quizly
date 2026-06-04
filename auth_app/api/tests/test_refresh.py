import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def api_client() -> APIClient:
    """Bereitet den APIClient fuer die Tests vor."""
    return APIClient()


@pytest.fixture
def refresh_url() -> str:
    """Gibt die URL fuer den Refresh-Endpunkt zurueck."""
    return reverse("token_refresh")


@pytest.fixture
def create_test_user() -> User:
    """Erstellt einen Test-User."""
    return User.objects.create_user(
        username="refreshuser",
        email="refresh@example.com",
        password="SecurePassword123",
    )


@pytest.mark.django_db
class TestTokenRefreshHappyPath:
    """Testet das erfolgreiche Erneuern des Access-Tokens."""

    def test_refresh_success(self, api_client, refresh_url, create_test_user) -> None:
        refresh = RefreshToken.for_user(create_test_user)
        api_client.cookies["refresh_token"] = str(refresh)

        response = api_client.post(refresh_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Token refreshed"
        assert "access_token" in response.cookies


@pytest.mark.django_db
class TestTokenRefreshUnhappyPath:
    """Testet Fehlerfälle beim Token-Refresh."""

    def test_refresh_missing_cookie(self, api_client, refresh_url) -> None:
        response = api_client.post(refresh_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_invalid_token(self, api_client, refresh_url) -> None:
        api_client.cookies["refresh_token"] = "invalid_token_string"
        response = api_client.post(refresh_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
