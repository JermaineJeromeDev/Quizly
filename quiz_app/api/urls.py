from django.urls import path

from .views import create_quiz_view

urlpatterns = [
    path("quizzes/", create_quiz_view, name="quiz_list_create"),
]
