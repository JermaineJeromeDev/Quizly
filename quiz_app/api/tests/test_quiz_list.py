import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from quiz_app.models import Question, Quiz
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def api_client() -> APIClient:
    """Prepare the APIClient instance for executing HTTP requests in tests."""
    return APIClient()


@pytest.fixture
def quiz_list_url() -> str:
    """Return the resolved URL path for the quiz creation and list endpoint."""
    return reverse("quiz_list_create")


@pytest.fixture
def logged_in_setup(api_client) -> tuple[APIClient, User]:
    """Create a test user and configure the API client with a valid cryptographic JWT access cookie."""
    user = User.objects.create_user(username="listuser", password="SecurePassword123")
    refresh = RefreshToken.for_user(user)
    api_client.cookies["access_token"] = str(refresh.access_token)
    return api_client, user


@pytest.mark.django_db
class TestQuizListHappyPath:
    """Contain all successful test scenarios related to retrieving the user's generated quiz overview list."""

    def test_get_quizzes_success(self, logged_in_setup, quiz_list_url) -> None:
        """Verify that an authorized user can successfully fetch an exhaustive list of their own quizzes."""
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
    """Contain all validation, constraint, and authentication failure scenarios for retrieving quiz lists."""

    def test_get_quizzes_unauthenticated(self, api_client, quiz_list_url) -> None:
        """Ensure that unauthenticated requests to view quiz catalogs are blocked with a 401 Unauthorized status."""
        response = api_client.get(quiz_list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
