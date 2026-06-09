import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from quiz_app.models import Quiz
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def api_client() -> APIClient:
    """Prepare the APIClient instance for executing HTTP requests in tests."""
    return APIClient()


@pytest.fixture
def logged_in_setup(api_client) -> tuple[APIClient, User]:
    """Create a test user and configure the API client with a valid cryptographic JWT access cookie."""
    user = User.objects.create_user(username="detailuser", password="SecurePassword123")
    refresh = RefreshToken.for_user(user)
    api_client.cookies["access_token"] = str(refresh.access_token)
    return api_client, user


@pytest.fixture
def create_own_quiz(logged_in_setup) -> Quiz:
    """Create and persist a test quiz record that belongs to the currently authenticated test user."""
    _, user = logged_in_setup
    return Quiz.objects.create(
        user=user,
        title="Mein eigenes Quiz",
        video_url="https://www.youtube.com/watch?v=example",
    )


@pytest.mark.django_db
class TestQuizDetailHappyPath:
    """Contain all successful test scenarios related to retrieving, updating, and deleting a user's own quiz."""

    def test_get_quiz_detail_success(self, logged_in_setup, create_own_quiz) -> None:
        """Verify that an authorized user can successfully fetch the detailed record of their own quiz."""
        client, _ = logged_in_setup
        url = reverse("quiz_detail", kwargs={"quiz_id": create_own_quiz.id})

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Mein eigenes Quiz"

    def test_patch_quiz_detail_success(self, logged_in_setup, create_own_quiz) -> None:
        """Verify that an authorized user can successfully partially update fields of their own quiz."""
        client, _ = logged_in_setup
        url = reverse("quiz_detail", kwargs={"quiz_id": create_own_quiz.id})
        payload = {"title": "Partially Updated Title"}

        response = client.patch(url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Partially Updated Title"
        assert response.data["description"] == create_own_quiz.description

    def test_delete_quiz_success(self, logged_in_setup, create_own_quiz) -> None:
        """Verify that an authorized user can successfully and permanently delete their own quiz record."""
        client, _ = logged_in_setup
        url = reverse("quiz_detail", kwargs={"quiz_id": create_own_quiz.id})

        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Quiz.objects.filter(id=create_own_quiz.id).exists()


@pytest.mark.django_db
class TestQuizDetailUnhappyPath:
    """Contain all validation, constraint, permission, and missing resource failure scenarios for quiz details."""

    def test_get_quiz_unauthenticated(self, api_client) -> None:
        """Ensure that unauthenticated requests to view quiz details are rejected with a 401 Unauthorized status."""
        url = reverse("quiz_detail", kwargs={"quiz_id": 1})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_quiz_foreign_forbidden(self, logged_in_setup) -> None:
        """Ensure that users are blocked with a 403 Forbidden status when attempting to access another user's quiz."""
        client, _ = logged_in_setup
        f_user = User.objects.create_user(username="foreign", password="Password123")
        f_quiz = Quiz.objects.create(
            user=f_user, title="Fremdes Quiz", video_url="https://url.com"
        )

        url = reverse("quiz_detail", kwargs={"quiz_id": f_quiz.id})
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_quiz_not_found(self, logged_in_setup) -> None:
        """Ensure that looking up a non-existent quiz ID correctly yields a 404 Not Found status."""
        client, _ = logged_in_setup
        url = reverse("quiz_detail", kwargs={"quiz_id": 9999})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_patch_quiz_foreign_forbidden(self, logged_in_setup) -> None:
        """Ensure that modification requests via PATCH on foreign quizzes are blocked with a 403 Forbidden status."""
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

    def test_delete_quiz_foreign_forbidden(self, logged_in_setup) -> None:
        """Ensure that deletion requests via DELETE on foreign quizzes are blocked with a 403 Forbidden status."""
        client, _ = logged_in_setup
        foreign_user = User.objects.create_user(
            username="intruder", password="Password123"
        )
        foreign_quiz = Quiz.objects.create(
            user=foreign_user, title="Fremdes Quiz", video_url="https://url.com"
        )

        url = reverse("quiz_detail", kwargs={"quiz_id": foreign_quiz.id})

        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Quiz.objects.filter(id=foreign_quiz.id).exists()
