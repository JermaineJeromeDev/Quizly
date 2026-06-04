from django.urls import path

from .views import login_user, logout_user, refresh_token_view, register_user

urlpatterns = [
    path("register/", register_user, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("refresh/", refresh_token_view, name="token_refresh"),
]
