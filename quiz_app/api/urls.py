from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import QuizGenerationStatusView, QuizViewSet

router = DefaultRouter()
router.register(r"quizzes", QuizViewSet, basename="quiz")

urlpatterns = [
    *router.urls,
    path(
        "quiz-generations/<uuid:pk>/",
        QuizGenerationStatusView.as_view(),
        name="quiz-generation-status",
    ),
]
