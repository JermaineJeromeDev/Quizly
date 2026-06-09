from auth_app.api.permissions import IsCookieAuthenticated
from django.shortcuts import get_object_or_404
from quiz_app.api.serializers import QuizCreateSerializer, QuizSerializer
from quiz_app.models import Question, Quiz
from quiz_app.services import generate_quiz_from_youtube
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response


class QuizViewSet(viewsets.ModelViewSet):
    """Provide a standard class-based ModelViewSet layer for managing AI-generated quizzes and nested questions."""

    serializer_class = QuizSerializer
    permission_classes = [IsCookieAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        """Isolate the query partition to return only quizzes belonging to the authenticated user context."""
        return Quiz.objects.filter(user=self.request.user).prefetch_related("questions")

    def get_object(self):
        """Enforce explicit ownership checks so foreign quizzes return 403 Forbidden instead of 404."""
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs.get(lookup_url_kwarg)
        quiz = get_object_or_404(Quiz, **{self.lookup_field: lookup_value})

        if quiz.user != self.request.user:
            raise PermissionDenied(detail="Zugriff verweigert.")

        return quiz

    def create(self, request, *args, **kwargs) -> Response:
        """Process incoming YouTube payload data to trigger audio downloads, Whisper transcription, and Gemini generation."""
        serializer = QuizCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        video_url = serializer.validated_data["url"]
        raw_quiz = generate_quiz_from_youtube(video_url)
        quiz = Quiz.objects.create(
            user=request.user,
            title=raw_quiz["title"],
            description=raw_quiz["description"],
            video_url=video_url,
        )

        for q_data in raw_quiz["questions"]:
            Question.objects.create(
                quiz=quiz,
                question_title=q_data["question_title"],
                question_options=q_data["question_options"],
                answer=q_data["answer"],
            )

        serializer = self.get_serializer(quiz)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
