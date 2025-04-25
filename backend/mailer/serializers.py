from rest_framework import serializers
from .models import EmailTemplate, EmailCampaign, EmailLog


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ["id", "name", "html_content", "created_at", "updated_at"]
        read_only_fields = ["user", "created_at", "updated_at"]


class EmailCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailCampaign
        fields = [
            "id",
            "name",
            "template",
            "csv_file",
            "email_field",
            "subject",
            "status",
            "total_emails",
            "sent_emails",
            "failed_emails",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "user",
            "status",
            "total_emails",
            "sent_emails",
            "failed_emails",
            "created_at",
            "updated_at",
        ]


class EmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailLog
        fields = [
            "id",
            "campaign",
            "recipient_email",
            "status",
            "error_message",
            "sent_at",
        ]
        read_only_fields = [
            "campaign",
            "recipient_email",
            "status",
            "error_message",
            "sent_at",
        ]
