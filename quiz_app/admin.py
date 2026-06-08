from django.contrib import admin

from .models import Question, Quiz


class QuestionInline(admin.TabularInline):
    """Ermöglicht das direkte Bearbeiten von Fragen innerhalb eines Quizzes."""

    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Konfiguriert die Quiz-Verwaltung im Admin-Panel."""

    list_display = ("title", "user", "created_at", "updated_at")
    search_fields = ("title", "description", "video_url")
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Konfiguriert die Fragen-Verwaltung im Admin-Panel."""

    list_display = ("question_title", "quiz", "answer", "created_at")
    search_fields = ("question_title", "answer")
    list_filter = ("quiz",)
