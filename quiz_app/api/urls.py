from django.urls import path

from .views import create_quiz_view, quiz_detail_view

urlpatterns = [
    path("quizzes/", create_quiz_view, name="quiz_list_create"),
    path("quizzes/<int:quiz_id>/", quiz_detail_view, name="quiz_detail"),
]
