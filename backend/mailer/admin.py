from django.contrib import admin
from .models import EmailCampaign, TagMapping, EmailLog


class TagMappingInline(admin.TabularInline):
    model = TagMapping
    extra = 1


class EmailLogInline(admin.TabularInline):
    model = EmailLog
    extra = 0
    readonly_fields = ("recipient_email", "sent_at", "success", "error_message")
    can_delete = False
    max_num = 0


@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "status",
        "total_emails",
        "sent_emails",
        "failed_emails",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("name", "user__email", "user__username")
    inlines = [TagMappingInline, EmailLogInline]
    readonly_fields = (
        "status",
        "total_emails",
        "sent_emails",
        "failed_emails",
        "created_at",
        "updated_at",
    )


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ("recipient_email", "campaign", "sent_at", "success")
    list_filter = ("success", "sent_at")
    search_fields = ("recipient_email", "campaign__name")
    readonly_fields = (
        "campaign",
        "recipient_email",
        "sent_at",
        "success",
        "error_message",
    )
