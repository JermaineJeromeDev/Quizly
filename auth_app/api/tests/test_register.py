import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    """Bereitet den APIClient fuer die Tests vor."""
    return APIClient()


@pytest.fixture
def registration_url() -> str:
    """Gibt die URL fuer den Registrierungs-Endpunkt zurueck."""
    return reverse("register")


@pytest.mark.django_db
class TestRegistrationHappyPath:
    """Umfasst alle erfolgreichen Szenarien fuer die Registrierung."""

    def test_registration_success(self, api_client, registration_url) -> None:
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
    """Umfasst alle Fehlerszenarien (Validierungsfehler, Duplikate)."""

    def test_registration_missing_fields(self, api_client, registration_url) -> None:
        payload = {"username": "testuser"}
        response = api_client.post(registration_url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.data

    def test_registration_password_mismatch(self, api_client, registration_url) -> None:
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePassword123",
            "confirmed_password": "WrongPassword",
        }
        response = api_client.post(registration_url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Passwörter stimmen nicht überein."
