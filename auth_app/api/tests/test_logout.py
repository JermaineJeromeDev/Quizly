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
def logout_url() -> str:
    """Return the resolved URL path for the authentication logout endpoint."""
    return reverse("logout")


@pytest.fixture
def create_logged_in_user(api_client) -> User:
    """Create a test user and simulate an authenticated session with active cookies."""
    user = User.objects.create_user(
        username="logoutuser", email="logout@example.com", password="SecurePassword123"
    )
    refresh = RefreshToken.for_user(user)
    api_client.cookies["access_token"] = str(refresh.access_token)
    api_client.cookies["refresh_token"] = str(refresh)
    return user


@pytest.mark.django_db
class TestLogoutHappyPath:
    """Contain all successful test scenarios related to user logout operations."""

    def test_logout_success(
        self, api_client, logout_url, create_logged_in_user
    ) -> None:
        """Verify that a successful logout blacklists the token and clears client cookies."""
        response = api_client.post(logout_url)
        expected_msg = "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == expected_msg

        assert response.cookies["access_token"].value == ""
        assert response.cookies["refresh_token"].value == ""


@pytest.mark.django_db
class TestLogoutUnhappyPath:
    """Contain all error and failure scenarios for invalid user logout attempts."""

    def test_logout_unauthenticated(self, api_client, logout_url) -> None:
        """Ensure unauthenticated logout requests are rejected with a 401 Unauthorized status."""
        response = api_client.post(logout_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
