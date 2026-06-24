from django.contrib import admin

from web.models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("text", "created_at")
    readonly_fields = ("created_at",)
