from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    """Bereitet den APIClient fuer die Tests vor."""
    return APIClient()


@pytest.fixture
def quiz_create_url() -> str:
    """Gibt die URL fuer den Quiz-Erstellungs-Endpunkt zurueck."""
    return reverse("quiz_list_create")


@pytest.fixture
def logged_in_client(api_client) -> APIClient:
    """Erstellt einen User und setzt das Access-Token im Cookie."""
    user = User.objects.create_user(username="quizuser", password="SecurePassword123")
    api_client.cookies["access_token"] = "mocked_valid_access_token"
    return api_client


@pytest.mark.django_db
class TestQuizCreateHappyPath:
    """Umfasst alle erfolgreichen Szenarien fuer die Quiz-Erstellung."""

    @patch("quiz_app.api.views.generate_quiz_from_youtube")
    def test_create_quiz_success(
        self, mock_generate, logged_in_client, quiz_create_url
    ) -> None:
        mock_generate.return_value = {
            "id": 1,
            "title": "KI-generiertes Quiz",
            "description": "Beschreibung des Quizzes",
            "video_url": "https://youtube.com",
            "questions": [
                {
                    "id": 1,
                    "question_title": "Welche Farbe hat der Himmel?",
                    "question_options": ["Blau", "Gruen", "Rot", "Gelb"],
                    "answer": "Blau",
                }
            ],
        }

        payload = {"url": "https://youtube.com"}
        response = logged_in_client.post(quiz_create_url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "KI-generiertes Quiz"
        assert len(response.data["questions"]) == 1
        assert (
            response.data["questions"][0]["question_title"]
            == "Welche Farbe hat der Himmel?"
        )


@pytest.mark.django_db
class TestQuizCreateUnhappyPath:
    """Umfasst alle Fehlerszenarien fuer die Quiz-Erstellung."""

    def test_create_quiz_unauthenticated(self, api_client, quiz_create_url) -> None:
        payload = {"url": "https://youtube.com"}
        response = api_client.post(quiz_create_url, payload, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_quiz_missing_url(self, logged_in_client, quiz_create_url) -> None:
        payload = {}
        response = logged_in_client.post(quiz_create_url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "url" in response.data
