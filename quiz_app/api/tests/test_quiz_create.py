from unittest.mock import patch

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
def quiz_create_url() -> str:
    """Return the resolved URL path for the quiz creation and list endpoint from the DRF router."""
    return reverse("quiz-list")


@pytest.fixture
def logged_in_client(api_client) -> APIClient:
    """Create a test user and configure the API client with a valid cryptographic JWT access cookie."""
    user = User.objects.create_user(username="quizuser", password="SecurePassword123")

    refresh = RefreshToken.for_user(user)
    api_client.cookies["access_token"] = str(refresh.access_token)
    return api_client


@pytest.mark.django_db
class TestQuizCreateHappyPath:
    """Contain all successful test scenarios related to AI-powered quiz generation."""

    @patch("quiz_app.api.views.generate_quiz_task.delay")
    def test_create_quiz_enqueues_generation(
        self, mock_task, logged_in_client, quiz_create_url
    ) -> None:
        """Verify valid requests are queued and return a pollable generation ID."""
        payload = {"url": "https://youtube.com"}
        response = logged_in_client.post(quiz_create_url, payload, format="json")

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.data["status"] == "pending"
        mock_task.assert_called_once_with(response.data["generation_id"])


@pytest.mark.django_db
class TestQuizCreateUnhappyPath:
    """Contain all validation, constraint, and authentication failure scenarios for quiz creation."""

    def test_create_quiz_unauthenticated(self, api_client, quiz_create_url) -> None:
        """Ensure that unauthenticated requests to generate a quiz are blocked with a 401 Unauthorized status."""
        payload = {"url": "https://youtube.com"}
        response = api_client.post(quiz_create_url, payload, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_quiz_missing_url(self, logged_in_client, quiz_create_url) -> None:
        """Ensure that requests with an empty payload or missing URL key are rejected with a 400 Bad Request status."""
        payload = {}
        response = logged_in_client.post(quiz_create_url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "url" in response.data
