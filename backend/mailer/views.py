from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from .serializers import EmailCampaignSerializer
from .models import EmailCampaign
from .utils import extract_tags_from_template, parse_excel_file
from .tasks import process_email_campaign


class EmailCampaignViewSet(viewsets.ModelViewSet):
    serializer_class = EmailCampaignSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EmailCampaign.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def start_campaign(self, request, pk=None):
        campaign = self.get_object()

        # Check if campaign is already processing or completed
        if campaign.status in ["processing", "completed"]:
            return Response(
                {
                    "status": "error",
                    "message": f"Campaign is already {campaign.status}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Start the campaign processing task
        process_email_campaign.delay(campaign.id)

        # Update status
        campaign.status = "processing"
        campaign.save()

        return Response(
            {"status": "success", "message": "Campaign started successfully"}
        )

    @action(detail=False, methods=["post"])
    def extract_template_tags(self, request):
        html_template = request.data.get("html_template", "")

        if not html_template:
            return Response(
                {"status": "error", "message": "HTML template is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tags = extract_tags_from_template(html_template)

        return Response({"status": "success", "tags": tags})

    @action(detail=False, methods=["post"])
    def validate_excel(self, request):
        excel_file = request.FILES.get("excel_file")

        if not excel_file:
            return Response(
                {"status": "error", "message": "Excel file is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Save the file temporarily
            temp_file_path = f"{settings.MEDIA_ROOT}/temp/{excel_file.name}"
            import os

            os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)

            with open(temp_file_path, "wb+") as destination:
                for chunk in excel_file.chunks():
                    destination.write(chunk)

            # Parse the Excel file
            df = parse_excel_file(temp_file_path)

            # Clean up the temp file
            os.remove(temp_file_path)

            # Return the headers
            return Response({"status": "success", "headers": df.columns.tolist()})
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
