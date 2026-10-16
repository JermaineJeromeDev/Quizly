from auth_app.api.permissions import IsCookieAuthenticated
from django.shortcuts import get_object_or_404
from kombu.exceptions import OperationalError
from quiz_app.api.serializers import QuizCreateSerializer, QuizSerializer
from quiz_app.models import Quiz, QuizGeneration
from quiz_app.tasks import generate_quiz_task
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView


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
        generation = QuizGeneration.objects.create(
            user=request.user,
            source_url=video_url,
        )
        try:
            generate_quiz_task.delay(str(generation.id))
        except OperationalError:
            generation.status = QuizGeneration.Status.FAILED
            generation.error_message = (
                "Der Hintergrunddienst ist momentan nicht erreichbar."
            )
            generation.save(
                update_fields=["status", "error_message", "updated_at"]
            )
            return Response(
                {"detail": generation.error_message},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {
                "generation_id": str(generation.id),
                "status": generation.status,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class QuizGenerationStatusView(APIView):
    """Return the authenticated user's generation state and completed quiz."""

    permission_classes = [IsCookieAuthenticated]

    def get(self, request, pk) -> Response:
        generation = get_object_or_404(
            QuizGeneration.objects.select_related("quiz").filter(user=request.user),
            pk=pk,
        )
        return Response(
            {
                "generation_id": str(generation.id),
                "status": generation.status,
                "error": generation.error_message or None,
                "quiz": QuizSerializer(generation.quiz).data
                if generation.quiz
                else None,
            }
        )
