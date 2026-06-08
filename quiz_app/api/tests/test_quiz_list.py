import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from quiz_app.models import Question, Quiz
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def api_client() -> APIClient:
    """Bereitet den APIClient fuer die Tests vor."""
    return APIClient()


@pytest.fixture
def quiz_list_url() -> str:
    """Gibt die URL fuer den Quiz-Listen-Endpunkt zurueck."""
    return reverse("quiz_list_create")


@pytest.fixture
def logged_in_setup(api_client) -> tuple[APIClient, User]:
    """Erstellt einen User und setzt ein echtes Access-Token im Cookie."""
    user = User.objects.create_user(username="listuser", password="SecurePassword123")
    refresh = RefreshToken.for_user(user)
    api_client.cookies["access_token"] = str(refresh.access_token)
    return api_client, user


@pytest.mark.django_db
class TestQuizListHappyPath:
    """Umfasst alle erfolgreichen Szenarien fuer das Abrufen der Quiz-Liste."""

    def test_get_quizzes_success(self, logged_in_setup, quiz_list_url) -> None:
        client, user = logged_in_setup

        quiz = Quiz.objects.create(
            user=user,
            title="Mein Test Quiz",
            description="Test Beschreibung",
            video_url="https://www.youtube.com/watch?v=example",
        )
        Question.objects.create(
            quiz=quiz,
            question_title="Test Frage?",
            question_options=["A", "B", "C", "D"],
            answer="A",
        )

        response = client.get(quiz_list_url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Mein Test Quiz"
        assert len(response.data[0]["questions"]) == 1


@pytest.mark.django_db
class TestQuizListUnhappyPath:
    """Umfasst alle Fehlerszenarien fuer das Abrufen der Quiz-Liste."""

    def test_get_quizzes_unauthenticated(self, api_client, quiz_list_url) -> None:
        response = api_client.get(quiz_list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
