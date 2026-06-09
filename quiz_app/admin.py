from django.contrib import admin

from .models import Question, Quiz


class QuestionInline(admin.TabularInline):
    """Enable inline editing and creation of nested Question records directly inside the Quiz administration view."""

    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Configure the layout, search metrics, and tabular inline representations for the Quiz model within the Django admin panel."""

    list_display = ("title", "user", "created_at", "updated_at")
    search_fields = ("title", "description", "video_url")
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Configure specialized list visualizations, structural filters, and search boundaries for individual Question models."""

    list_display = ("question_title", "quiz", "answer", "created_at")
    search_fields = ("question_title", "answer")
    list_filter = ("quiz",)
