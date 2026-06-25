from django.urls import path

from .views import LoginUserView, LogoutUserView, RefreshTokenView, RegisterUserView

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("login/", LoginUserView.as_view(), name="login"),
    path("logout/", LogoutUserView.as_view(), name="logout"),
    path("refresh/", RefreshTokenView.as_view(), name="token_refresh"),
]
