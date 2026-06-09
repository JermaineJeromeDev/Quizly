from quiz_app.models import Question, Quiz
from rest_framework import serializers


class QuestionSerializer(serializers.ModelSerializer):
    """Serialize question instances into the precisely specified nested JSON response format."""

    class Meta:
        model = Question
        fields = [
            "id",
            "question_title",
            "question_options",
            "answer",
            "created_at",
            "updated_at",
        ]


class QuizSerializer(serializers.ModelSerializer):
    """Serialize quiz instances including their cascade-nested question records for API delivery."""

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "video_url",
            "questions",
        ]


class QuizCreateSerializer(serializers.Serializer):
    """Validate the incoming payload used to generate a quiz from a YouTube URL."""

    url = serializers.URLField()
