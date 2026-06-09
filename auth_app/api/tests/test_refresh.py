import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def api_client() -> APIClient:
    """Prepare the APIClient instance for executing HTTP requests in tests."""
    return APIClient()


@pytest.fixture
def refresh_url() -> str:
    """Return the resolved URL path for the token refresh endpoint."""
    return reverse("token_refresh")


@pytest.fixture
def create_test_user() -> User:
    """Create and persist a standard test user profile inside the test database."""
    return User.objects.create_user(
        username="refreshuser",
        email="refresh@example.com",
        password="SecurePassword123",
    )


@pytest.mark.django_db
class TestTokenRefreshHappyPath:
    """Contain all successful test scenarios related to token refresh operations."""

    def test_refresh_success(self, api_client, refresh_url, create_test_user) -> None:
        """Verify that a valid refresh token cookie successfully generates a new access token cookie."""
        refresh = RefreshToken.for_user(create_test_user)
        api_client.cookies["refresh_token"] = str(refresh)

        response = api_client.post(refresh_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Token refreshed"
        assert "access_token" in response.cookies


@pytest.mark.django_db
class TestTokenRefreshUnhappyPath:
    """Contain all error and failure scenarios for token refresh attempts."""

    def test_refresh_missing_cookie(self, api_client, refresh_url) -> None:
        """Ensure token refresh requests fail with 401 if the refresh token cookie is missing."""
        response = api_client.post(refresh_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_invalid_token(self, api_client, refresh_url) -> None:
        """Ensure token refresh requests fail with 401 if the provided refresh token is malformed or invalid."""
        api_client.cookies["refresh_token"] = "invalid_token_string"
        response = api_client.post(refresh_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
