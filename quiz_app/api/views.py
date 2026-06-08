from auth_app.api.permissions import IsCookieAuthenticated
from quiz_app.api.serializers import QuizSerializer
from quiz_app.models import Question, Quiz
from quiz_app.services import generate_quiz_from_youtube
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


@api_view(["GET", "POST"])
@permission_classes([IsCookieAuthenticated])
def create_quiz_view(request) -> Response:
    """Verwaltet das Abrufen aller Quizzes (GET) und das Erstellen eines neuen Quizzes (POST)."""
    if request.method == "GET":
        quizzes = Quiz.objects.filter(user=request.user).prefetch_related("questions")
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    video_url = request.data.get("url")
    if not video_url:
        return Response(
            {"detail": "Ungültige URL oder Anfragedaten."},
            status=status.HTTP_400_BAD_REQUEST,
        )

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

    serializer = QuizSerializer(quiz)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsCookieAuthenticated])
def quiz_detail_view(request, quiz_id: int) -> Response:
    """Ruft ein spezifisches Quiz ab und prueft die Benutzerrechte (DoD-konform)."""
    try:
        quiz = Quiz.objects.prefetch_related("questions").get(id=quiz_id)
    except Quiz.DoesNotExist:
        return Response(
            {"detail": "Quiz nicht gefunden."}, status=status.HTTP_404_NOT_FOUND
        )

    if quiz.user != request.user:
        return Response(
            {"detail": "Zugriff verweigert."}, status=status.HTTP_403_FORBIDDEN
        )

    serializer = QuizSerializer(quiz)
    return Response(serializer.data, status=status.HTTP_200_OK)
