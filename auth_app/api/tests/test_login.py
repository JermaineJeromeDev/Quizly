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
def login_url() -> str:
    """Gibt die URL fuer den Login-Endpunkt zurueck."""
    return reverse("login")


@pytest.fixture
def create_test_user() -> User:
    """Erstellt einen Test-User in der Test-Datenbank."""
    return User.objects.create_user(
        username="loginuser", email="login@example.com", password="SecurePassword123"
    )


@pytest.mark.django_db
class TestLoginHappyPath:
    """Umfasst alle erfolgreichen Szenarien fuer den Login."""

    def test_login_success(self, api_client, login_url, create_test_user) -> None:
        payload = {"username": "loginuser", "password": "SecurePassword123"}
        response = api_client.post(login_url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Login successfully!"
        assert response.data["user"]["username"] == "loginuser"

        # Pruefen, ob die Cookies gesetzt wurden
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies
        assert response.cookies["access_token"]["httponly"] is True


@pytest.mark.django_db
class TestLoginUnhappyPath:
    """Umfasst alle Fehlerszenarien (falsche Daten)."""

    def test_login_invalid_credentials(
        self, api_client, login_url, create_test_user
    ) -> None:
        payload = {"username": "loginuser", "password": "WrongPassword"}
        response = api_client.post(login_url, payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == "Ungültige Anmeldedaten."
        assert "access_token" not in response.cookies
        assert "refresh_token" not in response.cookies
