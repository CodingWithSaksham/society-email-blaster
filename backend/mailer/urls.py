from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmailCampaignViewSet

router = DefaultRouter()
router.register(r"campaigns", EmailCampaignViewSet, basename="campaign")

urlpatterns = [
    path("", include(router.urls)),
]
