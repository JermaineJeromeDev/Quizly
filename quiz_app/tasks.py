import logging

from celery import shared_task
from django.db import transaction

from quiz_app.models import Question, Quiz, QuizGeneration
from quiz_app.services import generate_quiz_from_youtube

logger = logging.getLogger(__name__)


@shared_task(acks_late=True, reject_on_worker_lost=True)
def generate_quiz_task(generation_id: str) -> None:
    generation = QuizGeneration.objects.get(pk=generation_id)
    if generation.status == QuizGeneration.Status.SUCCEEDED:
        return
    generation.status = QuizGeneration.Status.PROCESSING
    generation.save(update_fields=["status", "updated_at"])

    try:
        raw_quiz = generate_quiz_from_youtube(generation.source_url)
        with transaction.atomic():
            quiz = Quiz.objects.create(
                user=generation.user,
                title=raw_quiz["title"],
                description=raw_quiz["description"],
                video_url=raw_quiz["formatted_video_url"],
            )
            Question.objects.bulk_create(
                [
                    Question(
                        quiz=quiz,
                        question_title=question["question_title"],
                        question_options=question["question_options"],
                        answer=question["answer"],
                    )
                    for question in raw_quiz["questions"]
                ]
            )
            generation.quiz = quiz
            generation.status = QuizGeneration.Status.SUCCEEDED
            generation.error_message = ""
            generation.save(
                update_fields=["quiz", "status", "error_message", "updated_at"]
            )
    except Exception:
        logger.exception("Quiz generation failed for %s", generation_id)
        generation.status = QuizGeneration.Status.FAILED
        generation.error_message = (
            "Die Quiz-Erstellung ist fehlgeschlagen. "
            "Bitte prüfe die Video-URL und versuche es erneut."
        )
        generation.save(update_fields=["status", "error_message", "updated_at"])
        raise
