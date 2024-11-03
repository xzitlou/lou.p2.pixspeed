from django.contrib import admin
from accounts.models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "verification_code",
        "api_token",
        "is_staff",
        "is_confirm",
        "is_plan_active",
        "plan_subscribed",
        "lang",
        "created_at",
    )
    readonly_fields = (
        "restore_password_token",
    )
    search_fields = (
        "email",
    )


admin.site.register(CustomUser, CustomUserAdmin)
