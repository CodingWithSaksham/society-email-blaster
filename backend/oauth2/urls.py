from django.urls import path
from .views import GoogleLoginView, GoogleAuthCallbackView

app_name = "oauth2"

urlpatterns = [
    path("login/", GoogleLoginView.as_view(), name="login"),
    path("google/callback/", GoogleAuthCallbackView.as_view(), name="callback"),
]
