from rest_framework import serializers
from .models import EmailCampaign, TagMapping, EmailLog


class TagMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagMapping
        fields = ["id", "template_tag", "excel_header"]


class EmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailLog
        fields = ["id", "recipient_email", "sent_at", "success", "error_message"]
        read_only_fields = fields


class EmailCampaignSerializer(serializers.ModelSerializer):
    tag_mappings = TagMappingSerializer(many=True, required=False)
    email_logs = EmailLogSerializer(many=True, read_only=True)

    class Meta:
        model = EmailCampaign
        fields = [
            "id",
            "name",
            "subject",
            "html_template",
            "excel_file",
            "created_at",
            "updated_at",
            "status",
            "total_emails",
            "sent_emails",
            "failed_emails",
            "tag_mappings",
            "email_logs",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "status",
            "total_emails",
            "sent_emails",
            "failed_emails",
        ]

    def create(self, validated_data):
        tag_mappings_data = validated_data.pop("tag_mappings", [])
        campaign = EmailCampaign.objects.create(**validated_data)

        for tag_mapping_data in tag_mappings_data:
            TagMapping.objects.create(campaign=campaign, **tag_mapping_data)

        return campaign
