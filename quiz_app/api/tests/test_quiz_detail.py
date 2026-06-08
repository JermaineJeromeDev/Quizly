import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from quiz_app.models import Quiz
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def api_client() -> APIClient:
    """Bereitet den APIClient fuer die Tests vor."""
    return APIClient()


@pytest.fixture
def logged_in_setup(api_client) -> tuple[APIClient, User]:
    """Erstellt einen User und setzt ein echtes Access-Token im Cookie."""
    user = User.objects.create_user(username="detailuser", password="SecurePassword123")
    refresh = RefreshToken.for_user(user)
    api_client.cookies["access_token"] = str(refresh.access_token)
    return api_client, user


@pytest.fixture
def create_own_quiz(logged_in_setup) -> Quiz:
    """Erstellt ein Quiz, das dem angemeldeten User gehoert."""
    _, user = logged_in_setup
    return Quiz.objects.create(
        user=user,
        title="Mein eigenes Quiz",
        video_url="https://www.youtube.com/watch?v=example",
    )


@pytest.mark.django_db
class TestQuizDetailHappyPath:
    """Testet das erfolgreiche Abrufen eines eigenen Quizzes."""

    def test_get_quiz_detail_success(self, logged_in_setup, create_own_quiz) -> None:
        client, _ = logged_in_setup
        url = reverse("quiz_detail", kwargs={"quiz_id": create_own_quiz.id})

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Mein eigenes Quiz"


@pytest.mark.django_db
class TestQuizDetailUnhappyPath:
    """Testet alle Fehlerszenarien (401, 403, 404)."""

    def test_get_quiz_unauthenticated(self, api_client) -> None:
        url = reverse("quiz_detail", kwargs={"quiz_id": 1})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_quiz_foreign_forbidden(self, logged_in_setup) -> None:
        client, _ = logged_in_setup
        f_user = User.objects.create_user(username="foreign", password="Password123")
        f_quiz = Quiz.objects.create(
            user=f_user, title="Fremdes Quiz", video_url="https://url.com"
        )

        url = reverse("quiz_detail", kwargs={"quiz_id": f_quiz.id})
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_quiz_not_found(self, logged_in_setup) -> None:
        client, _ = logged_in_setup
        url = reverse("quiz_detail", kwargs={"quiz_id": 9999})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestQuizDetailHappyPath:
    def test_patch_quiz_detail_success(self, logged_in_setup, create_own_quiz) -> None:
        """Testet das erfolgreiche partielle Updaten eines eigenen Quizzes."""
        client, _ = logged_in_setup
        url = reverse("quiz_detail", kwargs={"quiz_id": create_own_quiz.id})
        payload = {"title": "Partially Updated Title"}

        response = client.patch(url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Partially Updated Title"
        assert response.data["description"] == create_own_quiz.description


@pytest.mark.django_db
class TestQuizDetailUnhappyPath:
    def test_patch_quiz_foreign_forbidden(self, logged_in_setup) -> None:
        """Testet, dass man fremde Quizze nicht per PATCH manipulieren darf."""
        client, _ = logged_in_setup
        foreign_user = User.objects.create_user(
            username="stranger", password="Password123"
        )
        foreign_quiz = Quiz.objects.create(
            user=foreign_user, title="Fremdes Quiz", video_url="https://url.com"
        )

        url = reverse("quiz_detail", kwargs={"quiz_id": foreign_quiz.id})
        payload = {"title": "Hack-Versuch"}

        response = client.patch(url, payload, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN
