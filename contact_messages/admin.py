from django.contrib import admin

from contact_messages.models import Message


class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "message",
        "created_at",
    )
    readonly_fields = (
        "email",
        "message",
        "created_at"
    )


#admin.site.register(Message, MessageAdmin)
