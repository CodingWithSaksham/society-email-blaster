from django.urls import path, include
from .views import GoogleAuthInit, GoogleAuthCallback

urlpatterns = [
    path("login/", GoogleAuthInit.as_view()),
    path("callback/", GoogleAuthCallback.as_view()),
]
