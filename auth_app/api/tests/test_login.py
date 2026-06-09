import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    """Prepare the APIClient instance for executing HTTP requests in tests."""
    return APIClient()


@pytest.fixture
def login_url() -> str:
    """Return the resolved URL path for the authentication login endpoint."""
    return reverse("login")


@pytest.fixture
def create_test_user() -> User:
    """Create and persist a standard test user profile inside the test database."""
    return User.objects.create_user(
        username="loginuser", email="login@example.com", password="SecurePassword123"
    )


@pytest.mark.django_db
class TestLoginHappyPath:
    """Contain all successful test scenarios related to user login operations."""

    def test_login_success(self, api_client, login_url, create_test_user) -> None:
        """Verify that valid credentials correctly set secure HttpOnly authentication cookies."""
        payload = {"username": "loginuser", "password": "SecurePassword123"}
        response = api_client.post(login_url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Login successfully!"
        assert response.data["user"]["username"] == "loginuser"
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies
        assert response.cookies["access_token"]["httponly"] is True


@pytest.mark.django_db
class TestLoginUnhappyPath:
    """Contain all error and failure scenarios for invalid user login attempts."""

    def test_login_invalid_credentials(
        self, api_client, login_url, create_test_user
    ) -> None:
        """Ensure incorrect passwords trigger a 401 response and don't issue any auth cookies."""
        payload = {"username": "loginuser", "password": "WrongPassword"}
        response = api_client.post(login_url, payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == "Ungültige Anmeldedaten."
        assert "access_token" not in response.cookies
        assert "refresh_token" not in response.cookies
