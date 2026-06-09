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
def registration_url() -> str:
    """Return the resolved URL path for the user registration endpoint."""
    return reverse("register")


@pytest.mark.django_db
class TestRegistrationHappyPath:
    """Contain all successful test scenarios related to user registration operations."""

    def test_registration_success(self, api_client, registration_url) -> None:
        """Verify that providing all valid fields successfully creates a new user account."""
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePassword123",
            "confirmed_password": "SecurePassword123",
        }
        response = api_client.post(registration_url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["detail"] == "User created successfully!"
        assert User.objects.filter(username="testuser").exists()


@pytest.mark.django_db
class TestRegistrationUnhappyPath:
    """Contain all error and validation failure scenarios for user registration attempts."""

    def test_registration_missing_fields(self, api_client, registration_url) -> None:
        """Ensure that incomplete payloads are rejected with a 400 Bad Request status."""
        payload = {"username": "testuser"}
        response = api_client.post(registration_url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.data

    def test_registration_password_mismatch(self, api_client, registration_url) -> None:
        """Ensure that mismatched password fields fail validation and return a clear error message."""
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePassword123",
            "confirmed_password": "WrongPassword",
        }
        response = api_client.post(registration_url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Passwörter stimmen nicht überein."
