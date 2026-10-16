from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from kombu.exceptions import OperationalError
from quiz_app.models import Question, Quiz, QuizGeneration
from quiz_app.tasks import generate_quiz_task
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def authenticated_user() -> tuple[APIClient, User]:
    user = User.objects.create_user(
        username="generation-user", password="generation-test-password"
    )
    client = APIClient()
    access_token = RefreshToken.for_user(user).access_token
    client.cookies["access_token"] = str(access_token)
    return client, user


@pytest.mark.django_db
def test_generation_status_returns_completed_quiz(authenticated_user) -> None:
    client, user = authenticated_user
    quiz = Quiz.objects.create(
        user=user,
        title="Generated quiz",
        video_url="https://www.youtube.com/watch?v=example",
    )
    generation = QuizGeneration.objects.create(
        user=user,
        source_url="https://www.youtube.com/watch?v=example",
        status=QuizGeneration.Status.SUCCEEDED,
        quiz=quiz,
    )

    response = client.get(
        reverse("quiz-generation-status", kwargs={"pk": generation.id})
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == "succeeded"
    assert response.data["quiz"]["id"] == quiz.id


@pytest.mark.django_db
def test_generation_status_does_not_expose_other_users_generation(
    authenticated_user,
) -> None:
    client, _ = authenticated_user
    other_user = User.objects.create_user(
        username="another-user", password="generation-test-password"
    )
    generation = QuizGeneration.objects.create(
        user=other_user,
        source_url="https://www.youtube.com/watch?v=example",
    )

    response = client.get(
        reverse("quiz-generation-status", kwargs={"pk": generation.id})
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@patch(
    "quiz_app.api.views.generate_quiz_task.delay",
    side_effect=OperationalError("Redis unavailable"),
)
def test_create_quiz_returns_service_unavailable_when_broker_is_down(
    mock_task, authenticated_user
) -> None:
    client, _ = authenticated_user

    response = client.post(
        reverse("quiz-list"),
        {"url": "https://www.youtube.com/watch?v=example"},
        format="json",
    )

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert QuizGeneration.objects.get().status == QuizGeneration.Status.FAILED


@pytest.mark.django_db
@patch("quiz_app.tasks.generate_quiz_from_youtube")
def test_task_saves_quiz_and_marks_generation_complete(mock_generate) -> None:
    user = User.objects.create_user(
        username="task-user", password="generation-test-password"
    )
    generation = QuizGeneration.objects.create(
        user=user,
        source_url="https://www.youtube.com/watch?v=example",
    )
    mock_generate.return_value = {
        "title": "Generated quiz",
        "description": "Description",
        "formatted_video_url": "https://www.youtube.com/watch?v=example",
        "questions": [
            {
                "question_title": "Question?",
                "question_options": ["A", "B", "C", "D"],
                "answer": "A",
            }
        ],
    }

    generate_quiz_task.run(str(generation.id))
    generation.refresh_from_db()

    assert generation.status == QuizGeneration.Status.SUCCEEDED
    assert Quiz.objects.filter(pk=generation.quiz_id).exists()
    assert Question.objects.filter(quiz_id=generation.quiz_id).count() == 1


@pytest.mark.django_db
@patch(
    "quiz_app.tasks.generate_quiz_from_youtube",
    side_effect=RuntimeError("failed"),
)
def test_task_marks_generation_failed_and_reraises(mock_generate) -> None:
    user = User.objects.create_user(
        username="failed-task-user", password="generation-test-password"
    )
    generation = QuizGeneration.objects.create(
        user=user,
        source_url="https://www.youtube.com/watch?v=example",
    )

    with pytest.raises(RuntimeError, match="failed"):
        generate_quiz_task.run(str(generation.id))
    generation.refresh_from_db()

    assert generation.status == QuizGeneration.Status.FAILED
    assert generation.error_message
