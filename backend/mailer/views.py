import csv
import io
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import EmailTemplate, EmailCampaign, EmailLog
from .serializers import (
    EmailTemplateSerializer,
    EmailCampaignSerializer,
    EmailLogSerializer,
)
from .tasks import parse_template_tags, process_campaign


class IsAuthenticated(permissions.BasePermission):
    """
    Custom permission to only allow authenticated users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class EmailTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EmailTemplate.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get"])
    def tags(self, request, pk=None):
        template = self.get_object()
        tags = parse_template_tags(template.html_content)
        return Response({"tags": tags})


class EmailCampaignViewSet(viewsets.ModelViewSet):
    serializer_class = EmailCampaignSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EmailCampaign.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        campaign = self.get_object()

        if campaign.status not in ["pending", "failed"]:
            return Response(
                {"error": f"Campaign is already {campaign.status}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Start processing campaign in a separate thread
        import threading

        thread = threading.Thread(
            target=process_campaign, args=(campaign.id,), kwargs={"max_workers": 10}
        )
        thread.daemon = True
        thread.start()

        return Response({"status": "Campaign processing started"})

    @action(detail=True, methods=["get"])
    def preview_csv(self, request, pk=None):
        campaign = self.get_object()
        try:
            csv_file = campaign.csv_file.open("r")
            reader = csv.reader(io.StringIO(csv_file.read().decode("utf-8")))
            rows = list(reader)

            headers = rows[0] if rows else []
            data = rows[1:6] if len(rows) > 1 else []  # Preview first 5 rows

            return Response(
                {
                    "headers": headers,
                    "preview_rows": data,
                    "total_rows": len(rows) - 1 if rows else 0,
                }
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EmailLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EmailLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EmailLog.objects.filter(campaign__user=self.request.user)

    @action(detail=False, methods=["get"])
    def by_campaign(self, request):
        campaign_id = request.query_params.get("campaign_id")
        if not campaign_id:
            return Response(
                {"error": "campaign_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logs = EmailLog.objects.filter(
            campaign_id=campaign_id, campaign__user=request.user
        )
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
